from abc import abstractmethod
from dis import _HaveCodeOrStringType
from types import NoneType
import sqlparse
from typing import List, Optional, Tuple, Union
from enum import Enum, auto

class C(Enum):
    IDENTIFIER = auto()
    LITERAL = auto()
    KEYWORD = auto()
    OPERATOR = auto()
    SPECIAL_CHARACTER = auto()
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
    def _sep(cls, components: List[Token], separator: Token) -> List[Token]:
        result = components[0]
        for c in components[1:]:
            result += separator + c
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

class With(SQL):
    

    @override
    def __serialize(self):
        for query in self.queries:
            assert (
                query._alias is not None or query.c is not None
            ), "Every select in a with clause needs an alias"

        return "WITH\n" + self.indent(
            self.sep([q.render() for q in self.queries], ",\n")
        )

    def __init__(self, queries: List["Query"]):
        self.queries = queries
        self.c = c


class Query(SQL): # query_expr
    _with: Optional[With]
    _operation: Union[Select, "Query", SetOperation]
    _order_by: Optional[OrderBy]
    _limit: Optional[Limit]

    @override
    def __serialize(self) -> List[Token]:
        return self._chain(self._with, self._operation, self._order_by, self._limit)

    def __init__(
        self,
        WITH: Optional[Union[str, List["Query"], With]] = None,
        SELECT: Optional[Union[str, List[Col], Select]] = "*",
        FROM: Optional[Union[str, "Query", From]] = "",
        JOIN: Optional[Union[str, Tuple[Union[str, "Query"], JoinCondition], Join]] = None,
        WHERE: Optional[str] = None,
        GROUP_BY: Optional[str] = None,
        HAVING: Optional[str] = None,
        QUALIFY: Optional[str] = None,
        WINDOW: Optional[str] = None,
        ORDER_BY: Optional[str] = None,
        LIMIT: Optional[str] = None,
        # the rest of the join types go here to avoid cluttering the tooltip
    ):
        if isinstance(WITH, NoneType):
            self._with = None
        elif isinstance(WITH, str):
            self._with = With.raw(WITH)
        elif isinstance(WITH, List["Query"]):
            self._with = With(WITH)
        elif isinstance(WITH, With):
            self._with = WITH
        
        if isinstance(SELECT, str):
            # TODO this will need to take account of when user sets SELECT subfields in query constructor
            self._operation = Select.raw(SELECT)
        elif isinstance(SELECT, List[Col]):
            self._operation = Select(SELECT)
        elif isinstance(SELECT, Select):
            self._operation = SELECT

        self._order_by = OrderBy.raw(ORDER_BY) if ORDER_BY else None
        self._limit = Limit.raw(LIMIT) if LIMIT else None