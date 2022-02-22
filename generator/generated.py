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

# special charactor tokens
LP = Token("(", C.SPECIAL) # left-parenthesis
RP = Token(")", C.SPECIAL) # right-parenthesis
COMMA = Token(",", C.SPECIAL)

from typeguard import check_type
def matches_type(var, type):
    try:
        check_type('var', var, type)
        return True
    except (TypeError):
        return False
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

class LAST:
    _data: None
    def __init__(self, *args):
        self._data = ()


class FIRST:
    _data: None
    def __init__(self, *args):
        self._data = ()


class NULLS:
    _data: None
    def __init__(self, *args):
        self._data = ()


class DESC:
    _data: None
    def __init__(self, *args):
        self._data = ()


class ASC:
    _data: None
    def __init__(self, *args):
        self._data = ()


class EXCEPT:
    _data: None
    def __init__(self, *args):
        self._data = ()


class INTERSECT:
    _data: None
    def __init__(self, *args):
        self._data = ()


class DISTINCT:
    _data: None
    def __init__(self, *args):
        self._data = ()


class ALL:
    _data: None
    def __init__(self, *args):
        self._data = ()


class UNION:
    _data: None
    def __init__(self, *args):
        self._data = ()


class SELECT:
    _data: None
    def __init__(self, *args):
        self._data = ()


class EXP:
    _data: None
    def __init__(self, *args):
        self._data = ()


class WITH:
    _data: None
    def __init__(self, *args):
        self._data = ()


class OFFSET:
    _data: Tuple[EXP]
    def __init__(self, *args):
        self._data = (([arg for arg in args if matches_type(arg, EXP)] or [None])[0])


class LIMIT:
    _data: Tuple[EXP, OFFSET]
    def __init__(self, *args):
        self._data = (([arg for arg in args if matches_type(arg, EXP)] or [None])[0], ([arg for arg in args if matches_type(arg, OFFSET)] or [None])[0])


class ORDERBY:
    _data: Tuple[EXP, Optional[Union[ASC, DESC]], Optional[Tuple[NULLS, Union[FIRST, LAST]]]]
    def __init__(self, *args):
        self._data = (([arg for arg in args if matches_type(arg, EXP)] or [None])[0], ([arg for arg in args if matches_type(arg, Optional[Union[ASC, DESC]])] or [None])[0], ([arg for arg in args if matches_type(arg, Optional[Tuple[NULLS, Union[FIRST, LAST]]])] or [None])[0])


class QUERY:
    _data: Tuple[Optional[WITH], Union[SELECT, Tuple['QUERY'], Tuple['QUERY', Union[Tuple[UNION, Union[ALL, DISTINCT]], Tuple[INTERSECT, DISTINCT], Tuple[EXCEPT, DISTINCT]], 'QUERY']], Optional[ORDERBY], Optional[LIMIT]]
    def __init__(self, *args):
        self._data = (([arg for arg in args if matches_type(arg, Optional[WITH])] or [None])[0], ([arg for arg in args if matches_type(arg, Union[SELECT, Tuple[QUERY], Tuple[QUERY, Union[Tuple[UNION, Union[ALL, DISTINCT]], Tuple[INTERSECT, DISTINCT], Tuple[EXCEPT, DISTINCT]], QUERY]])] or [None])[0], ([arg for arg in args if matches_type(arg, Optional[ORDERBY])] or [None])[0], ([arg for arg in args if matches_type(arg, Optional[LIMIT])] or [None])[0])