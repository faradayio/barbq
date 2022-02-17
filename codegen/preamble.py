from typing import Any, List, Optional, Tuple, Union
from enum import Enum, auto

class C(Enum):
    IDENTIFIER = auto()
    LITERAL = auto()
    KEYWORD = auto()
    OPERATOR = auto()
    SPECIAL = auto()
    RAW = auto()

class Token:
    def __init__(self, data: Union[str, int], category: C):
        assert isinstance(data, str) or category == C.LITERAL, "nonliteral tokens cannot have nonstring type"
        self.data = data
        self.category = category

# keyword tokens
WITH = Token("WITH", C.KEYWORD)
RECURSIVE = Token("RECURSIVE", C.KEYWORD)
ORDER = Token("ORDER", C.KEYWORD)
BY = Token("BY", C.KEYWORD)
LIMIT = Token("LIMIT", C.KEYWORD)
ASC = Token("ASC", C.KEYWORD)
DESC = Token("DESC", C.KEYWORD)
LIMIT = Token("LIMIT", C.KEYWORD)
OFFSET = Token("OFFSET", C.KEYWORD)
SELECT = Token("SELECT", C.KEYWORD)
STRUCT = Token("STRUCT", C.KEYWORD)
VALUE = Token("VALUE", C.KEYWORD)
ALL = Token("ALL", C.KEYWORD)
DISTINCT = Token("DISTINCT", C.KEYWORD)
EXCEPT = Token("EXCEPT", C.KEYWORD)
REPLACE = Token("REPLACE", C.KEYWORD)
AS = Token("AS", C.KEYWORD)
FROM = Token("FROM", C.KEYWORD)
GROUP = Token("GROUP", C.KEYWORD)
HAVING = Token("HAVING", C.KEYWORD)
QUALIFY = Token("QUALIFY", C.KEYWORD)
WINDOW = Token("WINDOW", C.KEYWORD)
SYSTEM_TIME = Token("SYSTEM_TIME", C.KEYWORD)
OF = Token("OF", C.KEYWORD)
UNNEST = Token("UNNEST", C.KEYWORD)
UNPIVOT = Token("UNPIVOT", C.KEYWORD)
INCLUDE = Token("INCLUDE", C.KEYWORD)
NULLS = Token("NULLS", C.KEYWORD)
EXCLUDE = Token("EXCLUDE", C.KEYWORD)
FOR = Token("FOR", C.KEYWORD)
IN = Token("IN", C.KEYWORD)
CROSS = Token("CROSS", C.KEYWORD)
JOIN = Token("JOIN", C.KEYWORD)
INNER = Token("INNER", C.KEYWORD)
FULL = Token("FULL", C.KEYWORD)
OUTER = Token("OUTER", C.KEYWORD)
LEFT = Token("LEFT", C.KEYWORD)
RIGHT = Token("RIGHT", C.KEYWORD)
ON = Token("ON", C.KEYWORD)
USING = Token("USING", C.KEYWORD)
FIRST = Token("FIRST", C.KEYWORD)
LAST = Token("LAST", C.KEYWORD)
UNION = Token("UNION", C.KEYWORD)
INTERSECT = Token("INTERSECT", C.KEYWORD)

# special charactor tokens
LP = Token("(", C.SPECIAL) # left-parenthesis
RP = Token(")", C.SPECIAL) # right-parenthesis
COMMA = Token(",", C.SPECIAL)

class SQL:
    def __init__(self):
        self._raw = None

    def __str__(self) -> str:
        return self.render()

    def render(self) -> str:
        return " ".join([self._delex(token) for token in self._serialize()])

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
            if sql:
                result.extend(sql._serialize())
        return result

    @classmethod
    def _delex_root(cls, data: Any) -> str:
        if isinstance(data, str):
            return f"'{data}'"
        if isinstance(data, bool):
            return str(data).lower()
        if isinstance(data, list):
            return ", ".join([cls._delex_root(x) for x in data])
        if isinstance(data, tuple):
            return ", ".join([cls._delex_root(x) for x in data])
        raise Exception(f"unknown conversion for type: {type(data)}")

    @classmethod
    def _delex(cls, token: Token) -> str:
        if token.category == C.KEYWORD:
            return token.data
        if token.category == C.SPECIAL:
            return token.data
        if token.category == C.RAW:
            return token.data
        if token.category == C.OPERATOR:
            return token.data
        if token.category == C.LITERAL: # TODO more supported literal types to come
            if isinstance(token.data, int):
                return str(token.data)
            if isinstance(token.data, float):
                return str(token.data)
            if isinstance(token.data, list):
                return cls._delex_root(token.data)
            if isinstance(token.data, tuple):
                return cls._delex_root(token.data)
            if isinstance(token.data, dict):
                return cls._delex_root(token.data.values())
            if isinstance(token.data, bool):
                return str(token.data).lower()
            return f"'{token.data}'"
        if token.category == C.IDENTIFIER:
            return ".".join([f"`{path_component}`" for path_component in token.data.split(".")])
        raise Exception(f"unknown conversion for type: {type(token.data)}")

    def _serialize_(self) -> List[Token]:
        pass