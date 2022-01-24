from abc import abstractclassmethod, abstractmethod
from ntpath import join
from pydoc import text
from typing import List, Optional, Tuple, Union
from utils.locator_context import Locator

# https://cloud.google.com/bigquery/docs/reference/standard-sql/lexical


class SQL:
    def __init__(self, sql: Optional[str]):
        self.sql = sql

    def render(self) -> str:
        return self.sql if self.sql else ""

    @abstractclassmethod
    def raw(cls, text: str):
        pass

    @classmethod
    def indent(cls, text: str):
        return text.replace("\n", "\n    ")

    @classmethod
    def assert_at_most_one_set_and_get(cls, *args):
        real = [arg for arg in args if arg]
        assert len(real) < 2
        return None if len(real) == 0 else real[0]

    @classmethod
    def sep(cls, strings: List[str], separator: str):
        result = strings[0]
        for s in strings[1:]:
            result += separator + s


# TODO add intelligent discrimination to minimize quoting = maximize readability
class Ident(SQL):
    def __init__(self, text: Optional[str], c: Optional[str] = None):
        self.text = text if text else ""
        self.c = c

    def render(self):
        if self.c:
            return self.c
        if (
            self.text == "*" or True
        ):  # never quote because you can't quote table.col directly, need to break out by . TODO
            return self.text
        return "`" + self.text + "`"

    def __add__(self, other: "Ident"):
        return Ident(self.text + other.text)

    @classmethod
    def raw(cls, text: str):
        return Ident("", c=text)


class Lit(
    SQL
):  # TODO add automatic parsing depending on what python type we use to init
    def __init__(self, text: str, c: Optional[str] = None):
        self.text = text
        self.c = c

    def render(self):
        if self.c:
            return self.c
        return "'" + self.text + "'"

    @classmethod
    def raw(cls, text: str):
        return Lit("", c=text)


class Table(SQL):
    def __init__(
        self,
        name: Union[str, Locator],
        AS: Optional[str] = None,
        c: Optional[str] = None,
    ):
        if isinstance(name, str):
            self.name = Ident(name)
        else:
            self.name = Ident(name.get_project_and_path())
        self.alias = Ident(AS) if AS else None
        self.c = c

    def render(self):
        if self.c:
            return self.c
        result = self.name.render()
        if self.alias:
            result += " AS " + self.alias.render()
        return result

    def AS(self, alias: str):
        return Table(self.name.text, AS=alias)

    @classmethod
    def raw(cls, text):
        return Table("", c=text)


class Col(SQL):
    def __init__(
        self,
        name: str,
        table: Optional[Table] = None,
        AS: Optional[str] = None,
        c: Optional[str] = None,
    ):
        self.name = Ident(name)
        if table:
            self.name = table.name + self.name
        self.alias = Ident(AS) if AS else None
        self.c = c

    def render(self):
        if self.c:
            return self.c
        result = self.name.render()
        if self.alias:
            result += " AS " + self.alias.render()
        return result

    @classmethod
    def raw(cls, text):
        return Col("", c=text)


class Relation(SQL):
    def __init__(self, relation: Union[str, Table, "Query"], c: Optional[str] = None):
        if isinstance(relation, str):
            self.table = Table(relation)
        elif isinstance(relation, Table):
            self.table = relation
        else:
            self.query = relation
        self.c = c

    def render(self):
        if self.c:
            return self.c
        return (
            self.table.render()
            if self.table
            else self.indent("(\n" + self.query.render()) + "\n)"
        )

    @classmethod
    def raw(cls, text: str):
        return Relation("", c=text)


class JoinCondition(SQL):
    pass


class On(JoinCondition):
    def __init__(self, text: str):
        self._condition = SQL(text)

    def render(self):
        return self.indent(f"\nON {self._condition}")


class Using(JoinCondition):
    def __init__(self, cols: Union[Col, List[Col]]):
        if isinstance(cols, Col):
            cols = [cols]
        self._cols = cols

    def render(self):
        return f"\nUSING ({self.sep([col.render() for col in self._cols], ', ')})"


class Join(SQL):
    def __init__(
        self,
        table_condition: Tuple[Union[str, Table, "Query"], JoinCondition],
        type: str = "",
        c: Optional[str] = None,
    ):
        relation, self._join_condition = table_condition
        self._relation = Relation(relation)
        self.c = c

    def render(self):
        if self.c:
            return self.c
        return (
            f"{type+' '}JOIN {self._relation.render()} {self._join_condition.render()}"
        )

    @classmethod
    def raw(cls, text: str):
        return Join(("", On("")), c=text)


class Query(SQL):
    _with: Optional["With"]

    def __init__(
        self,
        *,
        WITH: Optional[Union["With", str, List["Query"]]] = None,
        SELECT: List[Col],
        FROM: Union[str, Table, "Query"],
        JOIN: Optional[Tuple[Union[str, Table, "Query"], JoinCondition]] = None,
        INNER_JOIN: Optional[Tuple[Union[str, Table, "Query"], JoinCondition]] = None,
        LEFT_JOIN: Optional[Tuple[Union[str, Table, "Query"], JoinCondition]] = None,
        RIGHT_JOIN: Optional[Tuple[Union[str, Table, "Query"], JoinCondition]] = None,
        FULL_JOIN: Optional[Tuple[Union[str, Table, "Query"], JoinCondition]] = None,
        WHERE: Optional[str] = None,
        GROUP_BY: Optional[str] = None,
        HAVING: Optional[str] = None,
        ORDER_BY: Optional[str] = None,
        LIMIT: Optional[str] = None,
        AS: Optional[str] = None,
        c: Optional[str] = None,
    ):
        if WITH:
            if isinstance(WITH, With):
                self._with = WITH
            elif isinstance(WITH, str):
                self._with = With.raw(WITH)
            else:
                self._with = With(WITH)
        else:
            self._with = None
        self._fields = SELECT
        self._from = Relation(FROM)
        join_arg = self.assert_at_most_one_set_and_get(
            JOIN, INNER_JOIN, LEFT_JOIN, RIGHT_JOIN, FULL_JOIN
        )
        self._join = Join(join_arg) if join_arg else None

        # for WHERE thru LIMIT, we just use raw SQL for now
        self._where = SQL(WHERE) if WHERE else None
        self._group_by = SQL(GROUP_BY) if GROUP_BY else None
        self._having = SQL(HAVING) if HAVING else None
        self._order_by = SQL(ORDER_BY) if ORDER_BY else None
        self._limit = SQL(LIMIT) if LIMIT else None

        self._alias = Ident(AS) if AS else None
        self.c = c

    def render(self):
        # as always, just use a string if we have one
        if self.c:
            return self.c
        result = "\n" + self._with.render() if self._with else ""
        result += "\nSELECT" + self.indent(
            f"\n{self.sep([f.render() for f in self._fields])}"
        )

        result += "\nFROM " + self._from.render()
        # all of the optional and unimplemented stuff
        result += "\n" + self._join.render() if self._join else ""
        result += "\nWHERE " + self._where.render() if self._where else ""
        result += "\nGROUP BY " + self._group_by.render() if self._group_by else ""
        result += "\nHAVING " + self._having.render() if self._having else ""
        result += "\nORDER BY " + self._order_by.render() if self._order_by else ""
        result += "\nLIMIT " + self._limit.render() if self._limit else ""
        if self._alias:
            return self._alias.render() + " AS (" + self.indent(result) + "\n)"
        return result

    @classmethod
    def raw(cls, text: str):
        return Query(SELECT=[], FROM="", c=text)


class With(SQL):
    """'A With clause is simply a list of tables required to have aliases"""

    def __init__(self, queries: List[Query], c: Optional[str] = None):
        self.queries = queries
        self.c = c

    def render(self):
        if self.c:
            return self.c

        for query in self.queries:
            assert (
                query._alias is not None or query.c is not None
            ), "Every select in a with clause needs an alias"

        return "WITH\n" + self.indent(
            self.sep([q.render() for q in self.queries], ",\n")
        )

    @classmethod
    def raw(cls, text: str):
        return With([], c=text)


basic_query = Query(
    SELECT=[
        Col("grannies.name", AS="who"),
        Col("specialty"),
        Col("grannies.hobby"),
    ],
    FROM=Table("acceptance-237317.kirby.grandmothers", AS="grannies"),
)

grandmothers = Table("acceptance-237317.kirby.grandmothers")
ref_scores = Table("acceptance-237317.kirby.ref_scores")

complex_query = Query(
    WITH=[
        Query(
            WITH=[
                Query(
                    SELECT=[
                        Col("name"),
                        Col.raw(
                            "CAST(hilda AS float64) + CAST(cookies AS float64) + CAST(knitting AS float64) AS hilda_score"
                        ),
                        Col.raw(
                            "CAST(mary AS float64) + CAST(bread as float64) + CAST(hockey AS float64) AS mary_score"
                        ),
                    ],
                    FROM=grandmothers,
                    AS="summary_scores",
                )
            ],
            SELECT=[
                Col("grannies.name", AS="name"),
                Col("hilda_score"),
                Col("mary_score"),
            ],
            FROM=grandmothers.AS("grannies"),
            JOIN=("summary_scores", On("summary_scores.name=grannies.name")),
            AS="scored_grandmas",
        ),
        Query.raw(
            f"combos AS (SELECT * FROM scored_grandmas CROSS JOIN {ref_scores.render()})"
        ),
    ],
    SELECT=[
        Col("brand"),
        Col("name", AS="granny"),
        Col.raw("relevance_score * mary_score AS score"),
    ],
    FROM="combos",
    WHERE="""
        granny='mary'
        -- for brands that care about similarity to mary, show how much they are interested in each of our grandmothers
    """,
)


# from uuid import uuid4

# source_table_id = uuid4()
# placespec_column_infos = [
#     {"col_name": "email", "used": True},
#     {"col_name": "first_name", "used": True},
#     {"col_name": "last_name", "used": False},
# ]
# loose_match_from_sql = "lm_table"
# proxy_table_name = "p_tab"
# mpjc = "sample_col"
# do_proxy_join = False
# pspec_table = "proxy" if do_proxy_join else "loose_match"
# print(
#     Query(
#         SELECT=[
#             Col(f"{pspec_table}.fdy_household_id", AS="fdy_household_id"),
#             Col.raw(f"'{source_table_id}' AS fdy_dataset_id"),
#         ]
#         + [
#             Col(f"{pspec_table}.{psci['col_name']}", AS=psci["col_name"])
#             if psci["used"]
#             else Col.raw(f"NULL AS {psci['col_name']}")
#             for psci in placespec_column_infos
#         ],
#         FROM=Table(loose_match_from_sql, AS="loose_match"),
#         JOIN=Join(
#             Table(proxy_table_name, AS="proxy"),
#             ON=f"loose_match.{mpjc}=proxy.{mpjc}",
#         )
#         if do_proxy_join
#         else None,
#     ).render()
# )

print(complex_query.render())

# TODO
# recreate the percentile code
# move to better named file, add to branch
# work with Thibault to test on the reporting SQL

# etsy prep
# set green
# set up env to run kickoff script

training_data_id = "a"
training_data_label = "a"
training_data_table = "a"
scores_id = "c"
scores_fold = "c"
scores_score = "d"
scores_table = "e"
positive_label = "f"

with_ = With([])

query = (
    Query(
        WITH=[
            Query(
                SELECT=[
                    Col("*"),
                    Col(f"training.label={positive_label}", AS="label_positive"),
                ],
                FROM="training",
                INNER_JOIN=(
                    Query(
                        SELECT=[
                            Col("id"),
                            Col.raw("ANY_VALUE(fold) AS fold"),
                            Col.raw("ANY_VALUE(score) AS score"),
                        ],
                        FROM="scores",
                        GROUP_BY="id",
                        AS="joined",
                    ),
                    Using(Col("id")),
                ),
            ),
            Query(
                SELECT=[
                    Col.raw(f"* EXCEPT ({training_data_id},{training_data_label})"),
                    Col(training_data_id, AS="id"),
                    Col(training_data_label, AS="label"),
                ],
                FROM=training_data_table,
                AS="training",
            ),
            Query(
                SELECT=[
                    Col(scores_id, AS="id"),
                    Col(scores_fold, AS="fold"),
                    Col(scores_score, AS="score"),
                ],
                FROM=scores_table,
                AS="scores",
            ),
        ],
        SELECT=[Col.raw("1")],
        FROM="",
    ),
)
print(query.render())



# A : B (D | E) (F)
class LiterateA(SQL):
    non_terminalB: LiterateB
    non_terminalC: Union[LiterateD, LiterateE]
    non_terminalF: Optional[LiterateF]
    terminal: str

    @override
    def rev_parse(self) -> List[Token]:
        pass
    @override
    def rev_lex(self, tokens: List[Token]) -> str/RawSql:
        pass
    def render(self):
        return self.rev_lex(self.rev_parse())
class Token:
    text: str
    type: identifier or special character or literal
    #https://cloud.google.com/bigquery/docs/reference/standard-sql/lexical