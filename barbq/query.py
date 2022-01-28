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
class CTE:
    self._cte_name: 

    def _serialize(self):
        return [Token(cte.AS, C.IDENTIFIER), Token("AS", C.KEYWORD), Token("(", C.SPECIAL)] + query._serialize() + [Token(")", C.SPECIAL)]
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

    # TODO START HERE the from nt has a lot of cases, it's a good time to take some time
    # to think about rules / conventions for translating from CFG to python objects
    # I also want to give my subconscious some time to decide what to do with aliases,
    # and to make sure I am not leading users into conceptual pitfalls in the way I
    # am setting up constructors. I need to clarify some design principles re CFG translation.
    
    # What variance do we allow in translation to support dialect ergonomics?

    # The other pressure on the formalism, both how we translate and how we render, is
    # the need to present reasonable options for composing queries as objects. There are two
    # canonical workflows that I want to support here:
    # 1. write megaquery->copy out chunks to named-objects/generator-func calls
    # 2. I am lazy->I want to reuse existing chunks and easily write SQL around them

    # this is normally not too bad, but the poor ergonomics of SQL bring it to light sometimes
    # as I've first seen when dealing with aliasing in with clauses. This is where I need to start
    # developing in parallel with someone translating, or preferably even multiple people
    def __init__(self):
        pass
class With(SQL): # with (interpolated)
    _ctes: List[CTE]

    def __serialize(self) -> List[Token]:
        return [Token("WITH", C.KEYWORD)] + self._sep([cte._serialize() for cte in self._ctes], Token(",", C.SPECIAL))

    def __init__(self, queries: List["Query"]):
        for query in queries:
            assert query.AS is not None, "Each query in a with clause needs an alias"
        self._ctes = queries
class Query(SQL): # query_expr
    _with: Optional[With]
    _operation: Union[Select, "Query", SetOperation]
    _order_by: Optional[OrderBy]
    _limit: Optional[Limit]
    AS: Optional[str] # publicly accessible, both for use by __serialize called on
            # an object that contains a Query or by the user 

    def AS(self, alias: str) -> None:
        self.AS = alias

    def __serialize(self) -> List[Token]:
        return self._chain(self._with, self._operation, self._order_by, self._limit)

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
        
        # select args
        match FROM:
            case None:
                from_ = From() # TODO should maybe make raw() smarter and then raise here
            case (str() | Query()) as arg:
                from_ = From(arg)
            case From() as from__:
                from_ = from__

        # _operation (only select for now)
        match SELECT:
            case (str() | [Col()]) as arg:
                self._operation = Select(arg, from_)
            case Select() as select:
                # TODO we should probably override any fields from the passed select if they are also set in the query constructor
                self._operation = select

        # unimplemented (class body = pass)
        self._order_by = OrderBy.raw(ORDER_BY) if ORDER_BY else None
        self._limit = Limit.raw(LIMIT) if LIMIT else None