from abc import abstractmethod
from dis import _HaveCodeOrStringType
import sqlparse
from typing import List, Optional, Tuple, Union
from enum import Enum, auto

class C(Enum):
    IDENTIFIER = auto()
    LITERAL = auto()
    KEYWORD = auto()
    OPERATOR = auto()
    SPECIAL = auto()
    RAW = auto()

class Token:
    def __init__(self, text: str, category: C):
        self.text = text
        self.category = category

# commonly used KEYWORD, OPERATOR, and SPECIAL tokens
AS = Token("AS", C.KEYWORD)
LP = Token("(", C.SPECIAL) # left-parenthesis
RP = Token(")", C.SPECIAL) # right-parenthesis
COMMA = Token(",", C.SPECIAL)

class SQL:
    def render(self) -> str:
        return sqlparse.format(" ".join([self._delex(token) for token in self._serialize()]))

    @classmethod
    def raw(cls, text: str):
        inst = cls()
        inst._raw = Token(text, C.RAW)
        return inst

    @classmethod
    def _sep(cls, components: List[List[Token]], separator: Token) -> List[Token]:
        result = components[0]
        for c in components[1:]:
            result += [separator] + c
        return result

    @classmethod
    def _chain(cls, components: List["SQL"]) -> List[Token]:
        result = []
        for sql in components:
            result.extend(sql._serialize())
        return result

    @classmethod
    def _table_or_query(cls, relation: Union["Table", "Query"]) -> List[Token]: # this probably shouldn't live here
        return relation._serialize() if isinstance(relation, Table) else [LP] + relation._serialize() + [RP]

    @classmethod
    def _delex(cls, token: Token) -> str:
        match token.category:
            case C.KEYWORD:
                return token.text
            case C.SPECIAL:
                return token.text
            case C.RAW:
                return token.text
            case C.OPERATOR:
                return token.text
            case C.LITERAL:
                return f"'{token.text}'"
            case C.IDENTIFIER:
                return "".join([f"`{path_component}`" for path_component in token.text.split(".")])


    @abstractmethod
    def __serialize(self) -> List[Token]:
        pass

    def _serialize(self) -> List[Token]:
        return [self._raw] if self._raw else self.__serialize()


class SetOperation(SQL):
    pass
class OrderBy(SQL):
    pass
class Limit(SQL):
    pass
class Where(SQL):
    pass
class GroupBy(SQL):
    pass
class Having(SQL):
    pass
class Qualify(SQL):
    pass
class Window(SQL):
    pass
class FromClause(SQL):
    pass
class Struct(SQL):
    pass
class Value(SQL):
    pass
class SelectMode(SQL):
    pass
class Using(SQL):
    pass
class On(SQL):
    pass
class Col(SQL):
    _text: str

    def __serialize(self) -> List[Token]:
        return [Token(self._text, C.IDENTIFIER)]

    def __init__(self, text: str):
        self._text = text
class Table(SQL): # yes, I know this is identical to Col for now
    _text: str
    def __serialize(self) -> List[Token]:
        return [Token(self._text, C.IDENTIFIER)]
    def __init__(self, text: str):
        self._text = text
class Join(SQL):
    _from_item: Union[Table, "Query"]
    _join_condition: Union[On, Using]

    def __serialize(self) -> List[Token]:
        return [Token("JOIN", C.KEYWORD)] + self._table_or_query(self._from_item) + self._join_condition._serialize()

    def __init__(self, args: Tuple[Union[Table, "Query"], Union[On, Using]]):
        self._from_item, self._join_condition = args
class From(SQL): # from (interpolated)
    _source: Union[Table, "Query"] # only 1 FromClause is supported right now

    def __serialize(self) -> List[Token]:
        return [Token("FROM", C.KEYWORD)] + self._table_or_query(self._source)

    def __init__(self, arg: Union[Table, "Query"]):
        self._source = arg
class Select(SQL):
    _nt1: Optional[Union[Struct, Value]]
    _nt2: Optional[SelectMode]
    _cols: List[Col] # this is provisional

    def __serialize(self) -> List[Token]:
        return [Token("SELECT", C.KEYWORD)] + self._sep([col._serialize() for col in self._cols], COMMA)

    def __init__(self, cols: Union[List[Col], str]):
        match cols:
            case [Col()] as cs:
                self._cols = cs
            case str as text:
                self._cols = [Col(text)]
class With(SQL): # with (interpolated)
    _queries: List["Query"]

    def __serialize(self) -> List[Token]:
        return [Token("WITH", C.KEYWORD)] + self._sep([cte._serialize() for cte in self._ctes], COMMA)

    def __init__(self, queries: List["Query"]):
        for query in queries:
            assert not (query._pre_alias is None and query._post_alias is None), "Each query in a with clause needs an alias"
            if query._post_alias:
                query._pre_alias = query._post_alias
                query._post_alias = None
        self._queries = queries
# select:
#     SELECT [ AS { STRUCT | VALUE } ] [{ ALL | DISTINCT }]
#         { [ expression. ]* [ EXCEPT ( column_name [, ...] ) ]
#             [ REPLACE ( expression [ AS ] column_name [, ...] ) ]
#         | expression [ [ AS ] alias ] } [, ...]
#     [ FROM from_clause[, ...] ]
#     [ WHERE bool_expression ]
#     [ GROUP BY { expression [, ...] | ROLLUP ( expression [, ...] ) } ]
#     [ HAVING bool_expression ]
#     [ QUALIFY bool_expression ]
#     [ WINDOW window_clause ]
# TODO document Col and Join CFG changes
class Query(SQL): # query_expr
    _with: Optional[With]
    _operation: Union[Select, "Query", SetOperation]
    _from: From
    _join: Optional[Join]
    _where: Optional[Where]
    _group_by: Optional[GroupBy]
    _having: Optional[Having]
    _qualify: Optional[Qualify]
    _order_by: Optional[OrderBy]
    _limit: Optional[Limit]
    _pre_alias: Optional[str]
    _post_alias: Optional[str]

    # syntactic sugar for changing or setting alias
    def AS(self, alias: str) -> None:
        self._post_alias = alias

    def __serialize(self) -> List[Token]:
        query = self._chain(
            self._with,
            self._operation,
            self._from,
            self._join,
            self._where,
            self._group_by,
            self._having,
            self._qualify,
            self._order_by,
            self._limit
        )
        assert self._pre_alias is None or self._post_alias is None, "Cannot have 2 aliases for 1 query. It should be impossible to get this error without directly modifying private fields"
        if self._pre_alias:
            return [Token(self._pre_alias, C.IDENTIFIER), AS, LP] + query + [RP]
        if self._post_alias:
            return query + [AS, Token(self._post_alias, C.IDENTIFIER)]
        return query

    # we always accept the type of the field, as well as any types
    # that can be reasonably interpreted as that type
    def __init__(
        self,
        WITH: Optional[Union[List["Query"], With]] = None,
        SELECT: Union[str, List[Col], Select] = "*",
        # these all technically belong to select
        FROM: Optional[Union[str, "Query", From]] = None,
        JOIN: Optional[Join] = None, # will be supported with something like the signature below in a (near-)future release
        # JOIN: Optional[Union[str, Tuple[Union[str, "Query"], JoinCondition], Join]] = None,
        WHERE: Optional[Where] = None,
        GROUP_BY: Optional[GroupBy] = None,
        HAVING: Optional[Having] = None,
        QUALIFY: Optional[Qualify] = None,
        WINDOW: Optional[Window] = None,
        # these two actually belong to a query in the grammar
        ORDER_BY: Optional[OrderBy] = None,
        LIMIT: Optional[Limit] = None,
        AS: Optional[str] = None,
        # the rest of the join types go here to avoid cluttering the tooltip
    ):
        # _with
        match WITH:
            case None:
                pass
            case [Query()] as queries:
                self._with = With(queries)
            case With() as raw:
                self._with = raw
        
        # _operation (only select for now)
        match SELECT:
            case (str() | [Col()]) as arg:
                self._operation = Select(arg)
            case Select() as select:
                self._operation = select

        # _from
        match FROM:
            case None:
                self._from = From() # TODO should maybe make raw() smarter and then raise here
            case (str() | Query()):
                self._from = From(FROM)
            case From():
                self._from = FROM

        # _join

        # _select args (raw only)
        self._where = WHERE
        self._group_by = GROUP_BY
        self._having = HAVING
        self._qualify = QUALIFY
        self._window = WINDOW

        # aliases
        self._post_alias = AS

        # query args (raw only)
        self._order_by = OrderBy.raw(ORDER_BY) if ORDER_BY else None
        self._limit = Limit.raw(LIMIT) if LIMIT else None