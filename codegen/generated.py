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

class Query(SQL):
	_field0: Optional[With]
	_field1: Union[Select, Query, QueryUnion[TokenUnion[Token, Token], TokenToken, TokenToken]Query]
	_field2: Optional[OrderBy]
	_field3: Optional[Limit]
    
    def _serialize_(self):
        result = []

        if blah:
            pass

        return result
    
    def __init__(self, 
a: None, b: None
):

        self._field1 = a



class OrderBy(SQL):

    
    def _serialize_(self):
        result = []

        if blah:
            pass

        return result
    
    def __init__(self, 
a: None, b: None
):

        self._field1 = a



class Limit(SQL):
	_field0: Exp
	_field1: Optional[Offset]
    
    def _serialize_(self):
        result = []

        if blah:
            pass

        return result
    
    def __init__(self, 
a: None, b: None
):

        self._field1 = a



class Offset(SQL):

    
    def _serialize_(self):
        result = []

        if blah:
            pass

        return result
    
    def __init__(self, 
a: None, b: None
):

        self._field1 = a



class With(SQL):

    
    def _serialize_(self):
        result = []

        if blah:
            pass

        return result
    
    def __init__(self, 
a: None, b: None
):

        self._field1 = a



class Cte(SQL):

    
    def _serialize_(self):
        result = []

        if blah:
            pass

        return result
    
    def __init__(self, 
a: None, b: None
):

        self._field1 = a



class RecursiveCte(SQL):

    
    def _serialize_(self):
        result = []

        if blah:
            pass

        return result
    
    def __init__(self, 
a: None, b: None
):

        self._field1 = a



class Select(SQL):
	_field0: Optional[TokenUnion[Token, Token]]Optional[Union[Token, Token]]
	_field1: {...Union[Optional[Exp.]*Optional[Except]Optional[Replace], ExpOptional[As]]...}
	_field2: Optional[From]
	_field3: Optional[Where]
	_field4: Optional[GroupBy]
	_field5: Optional[Having]
	_field6: Optional[Qualify]
	_field7: Optional[Window]
    
    def _serialize_(self):
        result = []

        if blah:
            pass

        return result
    
    def __init__(self, 
a: None, b: None
):

        self._field1 = a



class Except(SQL):

    
    def _serialize_(self):
        result = []

        if blah:
            pass

        return result
    
    def __init__(self, 
a: None, b: None
):

        self._field1 = a



class Replace(SQL):

    
    def _serialize_(self):
        result = []

        if blah:
            pass

        return result
    
    def __init__(self, 
a: None, b: None
):

        self._field1 = a



class Where(SQL):

    
    def _serialize_(self):
        result = []

        if blah:
            pass

        return result
    
    def __init__(self, 
a: None, b: None
):

        self._field1 = a



class GroupBy(SQL):

    
    def _serialize_(self):
        result = []

        if blah:
            pass

        return result
    
    def __init__(self, 
a: None, b: None
):

        self._field1 = a



class Having(SQL):

    
    def _serialize_(self):
        result = []

        if blah:
            pass

        return result
    
    def __init__(self, 
a: None, b: None
):

        self._field1 = a



class Qualify(SQL):

    
    def _serialize_(self):
        result = []

        if blah:
            pass

        return result
    
    def __init__(self, 
a: None, b: None
):

        self._field1 = a



class Window(SQL):

    
    def _serialize_(self):
        result = []

        if blah:
            pass

        return result
    
    def __init__(self, 
a: None, b: None
):

        self._field1 = a



class From(SQL):

    
    def _serialize_(self):
        result = []

        if blah:
            pass

        return result
    
    def __init__(self, 
a: None, b: None
):

        self._field1 = a



class Relation(SQL):

    
    def _serialize_(self):
        result = []

        if blah:
            pass

        return result
    
    def __init__(self, 
a: None, b: None
):

        self._field1 = a



class ForSystemTimeAsOf(SQL):

    
    def _serialize_(self):
        result = []

        if blah:
            pass

        return result
    
    def __init__(self, 
a: None, b: None
):

        self._field1 = a



class As(SQL):

    
    def _serialize_(self):
        result = []

        if blah:
            pass

        return result
    
    def __init__(self, 
a: None, b: None
):

        self._field1 = a



class unnest_operator(SQL):
	_field0: Union[
	_field1: UNNEST(Exp(array)
	_field2: , UNNEST(array_path
	_field3: , array_path
	_field4: ]
	_field5: Optional[As]
	_field6: Optional[TokenTokenOptional[alias]]
    
    def _serialize_(self):
        result = []

        if blah:
            pass

        return result
    
    def __init__(self, 
a: None, b: None
):

        self._field1 = a



class Unpivot(SQL):
	_field0: Optional[Union[TokenToken, TokenToken]]
	_field1: Union[single_column_unpivot, multi_column_unpivot]Optional[As]
    
    def _serialize_(self):
        result = []

        if blah:
            pass

        return result
    
    def __init__(self, 
a: None, b: None
):

        self._field1 = a



class single_column_unpivot(SQL):
	_field0: Exp(col)
	_field1: TokenExp(col)
	_field2: Token(columns_to_unpivot)
    
    def _serialize_(self):
        result = []

        if blah:
            pass

        return result
    
    def __init__(self, 
a: None, b: None
):

        self._field1 = a



class multi_column_unpivot(SQL):
	_field0: {...Exp(col)...}
	_field1: TokenExp(col)
	_field2: Tokencolumn_sets_to_unpivot
    
    def _serialize_(self):
        result = []

        if blah:
            pass

        return result
    
    def __init__(self, 
a: None, b: None
):

        self._field1 = a



class In(SQL):
	_field0: For:Exp(col)
    
    def _serialize_(self):
        result = []

        if blah:
            pass

        return result
    
    def __init__(self, 
a: None, b: None
):

        self._field1 = a



class columns_to_unpivot(SQL):

    
    def _serialize_(self):
        result = []

        if blah:
            pass

        return result
    
    def __init__(self, 
a: None, b: None
):

        self._field1 = a



class column_sets_to_unpivot(SQL):

    
    def _serialize_(self):
        result = []

        if blah:
            pass

        return result
    
    def __init__(self, 
a: None, b: None
):

        self._field1 = a



class On(SQL):
	_field0: Using:{...Exp...}
    
    def _serialize_(self):
        result = []

        if blah:
            pass

        return result
    
    def __init__(self, 
a: None, b: None
):

        self._field1 = a



class Relation(SQL):
	_field0: INNER_JOIN:Union[On, Using]
	_field1: JOIN:Union[On, Using]
	_field2: FULL_OUTER_JOIN:Union[On, Using]
	_field3: FULL_JOIN:Union[On, Using]
	_field4: LEFT_OUTER_JOIN:Union[On, Using]
	_field5: LEFT_JOIN:Union[On, Using]
	_field6: RIGHT_OUTER_JOIN:Union[On, Using]
	_field7: RIGHT_JOIN:Union[On, Using]
	_field8: CROSS_JOIN:
	_field9: Exp:
	_field10: connectorfuncsforallops
	_field11: subclassing
	_field12: funcs
	_field13: pivot
	_field14: alias
	_field15: Relations,select,CTEs
	_field16: stringinputs/tablenames
	_field17: recursivewith
	_field18: windowexpressions
	_field19: keyforthegrammar
    
    def _serialize_(self):
        result = []

        if blah:
            pass

        return result
    
    def __init__(self, 
a: None, b: None
):

        self._field1 = a

