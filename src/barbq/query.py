from abc import abstractclassmethod, abstractmethod
from ntpath import join
from pydoc import text
from typing import List, Optional, Tuple, Union

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
        return text.replace("\n", "\n    ") if text else None

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
        return result

class Ident(SQL):
    def __init__(self, text: Optional[str], c: Optional[str] = None):
        self.text = text if text else ""
        self.c = c

    def render(self):
        if self.c:
            return self.c
        if (
            self.text == "*" or True
        ):
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
        name: str,
        AS: Optional[str] = None,
        c: Optional[str] = None,
    ):
        self.name = Ident(name)
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
        self.table = None
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
        mode: str = "",
        c: Optional[str] = None,
    ):
        relation, self._join_condition = table_condition
        self._relation = Relation(relation)
        self.c = c
        self.mode = mode

    def render(self):
        if self.c:
            return self.c
        return (
            f"{self.mode+' '}JOIN {self._relation.render()} {self._join_condition.render()}"
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
            f"\n{self.sep([f.render() for f in self._fields], ',')}"
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

        if self.queries is None:
            return ""

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