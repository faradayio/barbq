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

class SQL:
    def render(self) -> str:
        return sqlparse.format(self._delex(self._serialize()))

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
    def _chain(components: List["SQL"]) -> List[Token]:
        result = []
        for sql in components:
            result.extend(sql._serialize())
        return result

    @classmethod
    def _delex(cls, tokens: List[Token]) -> str:
        pass # TODO

    @abstractmethod
    def __serialize(self) -> List[Token]:
        pass

    def _serialize(self) -> List[Token]:
        return [self._raw] if self._raw else self.__serialize()


class Col:
    pass
class Select:
    pass
class SetOperation:
    pass
class OrderBy:
    pass
class Limit:
    pass
class JoinCondition:
    pass
class Join:
    pass
class Select:
    pass
class Where:
    pass
class GroupBy:
    pass
class Having:
    pass
class Qualify:
    pass
class Window:
    pass
class FromClause:
    pass
# anything interpolated is only added so users can pass these objects around
# for lesser used features, interpolated nonterminals will probably not be created
class From: # from (interpolated)
    _from_clauses: List[FromClause]

    def __serialize(self) -> List[Token]:
        pass

    def __init__(self):
        pass
class With(SQL): # with (interpolated)
    _queries: List["Query"]

    def __serialize(self) -> List[Token]:
        return [Token("WITH", C.KEYWORD)] + self._sep([cte._serialize() for cte in self._ctes], Token(",", C.SPECIAL))

    def __init__(self, queries: List["Query"]):
        for query in queries:
            assert not (query._pre_alias is None and query._post_alias is None), "Each query in a with clause needs an alias"
            if query._post_alias:
                query._pre_alias = query._post_alias
                query._post_alias = None
        self._queries = queries
class Query(SQL): # query_expr
    _with: Optional[With]
    _operation: Union[Select, "Query", SetOperation]
    _order_by: Optional[OrderBy]
    _limit: Optional[Limit]
    _pre_alias: Optional[str]
    _post_alias: Optional[str]

    # syntactic sugar for changing or setting alias
    def AS(self, alias: str) -> None:
        self._post_alias = alias

    def __serialize(self) -> List[Token]:
        query = self._chain(self._with, self._operation, self._order_by, self._limit)
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
                self._operation = Select(arg, from_)
            case Select() as select:
                # TODO we should probably override any fields from the passed select if they are also set in the query constructor
                self._operation = select

        # select args
        match FROM:
            case None:
                from_ = From() # TODO should maybe make raw() smarter and then raise here
            case (str() | Query()) as arg:
                from_ = From(arg)
            case From() as from__:
                from_ = from__


        # aliases


        # unimplemented (class body = pass)
        self._order_by = OrderBy.raw(ORDER_BY) if ORDER_BY else None
        self._limit = Limit.raw(LIMIT) if LIMIT else None