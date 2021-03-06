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
        return sqlparse.format(" ".join([self._delex(token) for token in self._serialize()]))

    @classmethod
    def raw(cls, text: str):
        try:
            inst = cls()
        except:
            try:
                inst = cls("")
            except:
                try:
                    inst = cls(Table.raw(""))
                except:
                    inst = cls(FROM=Table.raw(""))
        inst._raw = text
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
            if sql:
                result.extend(sql._serialize())
        return result

    @classmethod
    def _table_or_query(cls, relation: Union["Table", "Query"]) -> List[Token]: # this probably shouldn't live here
        return relation._serialize() if isinstance(relation, Table) else [LP] + relation._serialize() + [RP]

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
    def _serialize(self) -> List[Token]:
        return [Token(self._raw, C.RAW)] if self._raw else self._serialize_()

# to support interpolating other SQL objects into expressions, which we otherwise
# don't parse yet, SQL will override __str__ to shadow render
class Exp(SQL):
    _expression: Union[str, Tuple["Exp", Token, "Exp"]]
    
    def _serialize_(self) -> List[Token]:
        if isinstance(self._expression, str):
            return [Token(self._expression, C.RAW)]
        else:
            return [LP] + self._expression[0]._serialize() + [self._expression[1]] + self._expression[2]._serialize() + [RP]
    
    def __init__(self, expression: str):
        super().__init__()
        self._expression = expression # TODO add some basic validation here

    def __and__(self, exp: Union[str, "Exp"]) -> "Exp": # add column as potential input
        result_exp = Exp("")
        result_exp._expression = (
            self,
            AND,
            exp if isinstance(exp, "Exp") else Exp(exp)
        )
        return result_exp

    def __or__(self, exp: Union[str, "Exp"]) -> "Exp": # add column as potential input
        result_exp = Exp("")
        result_exp._expression = (
            self,
            OR,
            exp if isinstance(exp, Exp) else Lit(exp)
        )
        return result_exp

class Func(Exp):
    pass

class ARRAY_CONCAT(Func):
    _exp: Exp

    def _serialize(self) -> List[Token]:
        return [Token("ARRAY_CONCAT", C.KEYWORD), LP] + self._exp._serialize() + [RP]

    def __init__(self, exp: Union[str, Exp]):
        self._exp = Exp(exp)

class ARRAY_LENGTH(Func):
    _exp: Exp

    def _serialize(self) -> List[Token]:
        return [Token("ARRAY_LENGTH", C.KEYWORD), LP] + self._exp._serialize() + [RP]

    def __init__(self, exp: Union[str, Exp]):
        self._exp = Exp(exp)

class ARRAY_TO_STRING(Func):
    _exp: Exp

    def _serialize(self) -> List[Token]:
        return [Token("ARRAY_TO_STRING", C.KEYWORD), LP] + self._exp._serialize() + [RP]

    def __init__(self, exp: Union[str, Exp]):
        self._exp = Exp(exp)

class GENERATE_ARRAY(Func):
    _exp: Exp

    def _serialize(self) -> List[Token]:
        return [Token("GENERATE_ARRAY", C.KEYWORD), LP] + self._exp._serialize() + [RP]

    def __init__(self, exp: Union[str, Exp]):
        self._exp = Exp(exp)

class GENERATE_DATE_ARRAY(Func):
    _exp: Exp

    def _serialize(self) -> List[Token]:
        return [Token("GENERATE_DATE_ARRAY", C.KEYWORD), LP] + self._exp._serialize() + [RP]

    def __init__(self, exp: Union[str, Exp]):
        self._exp = Exp(exp)

class GENERATE_TIMESTAMP_ARRAY(Func):
    _exp: Exp

    def _serialize(self) -> List[Token]:
        return [Token("GENERATE_TIMESTAMP_ARRAY", C.KEYWORD), LP] + self._exp._serialize() + [RP]

    def __init__(self, exp: Union[str, Exp]):
        self._exp = Exp(exp)

class ARRAY_REVERSE(Func):
    _exp: Exp

    def _serialize(self) -> List[Token]:
        return [Token("ARRAY_REVERSE", C.KEYWORD), LP] + self._exp._serialize() + [RP]

    def __init__(self, exp: Union[str, Exp]):
        self._exp = Exp(exp)

class OVER(Func):
    _partition_by: Exp
    _order_by: Optional[Exp]

    def _serialize_(self) -> List[Token]:
        return [Token("OVER", C.KEYWORD), LP, Token("PARTITION", C.KEYWORD), BY] + self._partition_by._serialize() + ([Token("ORDER", C.KEYWORD), BY] + self._order_by._serialize() if self._order_by else []) + [RP]

    def __init__(
        self,
        PARTITION_BY: Optional[Union[str, Exp]] = None,
        ORDER_BY: Optional[Union[str, Exp]] = None,
    ):
        self._partition_by = Exp(PARTITION_BY)
        self._order_by = Exp(ORDER_BY)

print((Exp("exp1") & Exp("exp2")).render()) # exp1 AND exp2

class Lit(Exp):
    pass
class Col(Exp):
    _text: Union[str, Exp]
    _alias: Optional[str]

    # syntactic sugar for changing or setting alias
    def AS(self, alias: str) -> None:
        self._alias = alias
        return self

    def _serialize_(self) -> List[Token]:
        return ([Token(self._text, C.SPECIAL) if self._text == "*" else Token(self._text, C.IDENTIFIER)] if isinstance(self._text, str) else self._text._serialize()) + ([AS, Token(self._alias, C.IDENTIFIER)] if self._alias else [])

    def __init__(self, text: Union[str, Exp], AS: Optional[str] = None):
        super().__init__()
        self._text = text
        self._alias = AS
class Case(SQL):
    _cases: List["Exp"]
    _else: Optional["Exp"]

    def _serialize_(self) -> List[Token]:
        result = [Token("CASE", C.KEYWORD)]
        for c in self._cases:
            result += [Token("WHEN", C.KEYWORD)] + c._serialize()
        if self._else:
            result += [Token("ELSE", C.KEYWORD)] + self._else._serialize()
        result += [Token("END", C.KEYWORD)]
        return result

    def __init__(self, CASE: List["Exp"], ELSE: Optional["Exp"]=None):
        super().__init__()
        self._cases = CASE
        self._else = ELSE

class SetOperation(SQL):
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

class OrderBy(SQL):
    _col: Col
    _order: Optional[Token]

    def _serialize_(self) -> List[Token]:
        result = self._col._serialize()
        if self._order:
            result += [self._order]
        return result
    
    def __init__(self, col: Col, order: Optional[Token] = None):
        super().__init__()
        self._col = col
        assert order is None or order.data == "ASC" or order.data == "DESC"
        self._order = order

class OrderBys(SQL):
    _orderbys: List[OrderBy]

    def _serialize_(self) -> List[Token]:
        return [Token("ORDER", C.KEYWORD), BY] + self._sep([orderby._serialize_() for orderby in self._orderbys], COMMA)

    def __init__(self, orderbys: List[OrderBy]):
        super().__init__()
        self._orderbys = orderbys

class Limit(SQL):
    _limit: int

    def _serialize_(self) -> List[Token]:
        return [Token("LIMIT", C.KEYWORD), Token(self._limit, C.LITERAL)]
    
    def __init__(self, limit: int):
        super().__init__()
        self._limit = limit
class Using(SQL):
    _col: Col

    def _serialize_(self) -> List[Token]:
        return [Token("USING", C.KEYWORD)] + self._col._serialize()

    def __init__(self, col: Col):
        super().__init__()
        self._col = col

class On(SQL):
    _col1: Col
    _col2: Col

    def _serialize_(self) -> List[Token]:
        return [Token("ON", C.KEYWORD)] + self._col1._serialize() + [Token("=", C.OPERATOR)] + self._col2._serialize()
    
    def __init__(self, col1: Col, col2: Col):
        super().__init__()
        self._col1 = col1
        self._col2 = col2

class Where(SQL):
    _exp: Exp

    def _serialize_(self) -> List[Token]:
        return [Token("WHERE", C.KEYWORD)] + self._exp._serialize()

    def __init__(self, exp: Exp):
        super().__init__()
        self._exp = exp
class GroupBy(SQL):
    _exps: List[Exp]

    def _serialize_(self) -> List[Token]:
        return [Token("GROUP", C.KEYWORD), BY] + self._sep([exp._serialize_() for exp in self._exps], COMMA)
    
    def __init__(self, exps: Union[Exp, List[Exp]]):
        super().__init__()
        if isinstance(exps, Exp):
            self._exps = [exps]
        else:
            self._exps = exps

class Table(SQL): # yes, I know this is identical to Col for now
    _text: str
    _alias: Optional[str]

    # syntactic sugar for changing or setting alias
    def AS(self, alias: str) -> None:
        self._alias = alias
        return self

    def _serialize_(self) -> List[Token]:
        return [Token(self._text, C.IDENTIFIER)] + ([AS, Token(self._alias, C.IDENTIFIER)] if self._alias else [])

    def __init__(self, text: str, AS: Optional[str] = None):
        super().__init__()
        self._text = text
        self._alias = AS
class Join(SQL):
    _from_item: Union[Table, "Query"]
    _join_condition: Union[On, Using]

    def _serialize_(self) -> List[Token]:
        return [Token("JOIN", C.KEYWORD)] + self._table_or_query(self._from_item) + self._join_condition._serialize()

    def __init__(self, args: Tuple[Union[Table, "Query"], Union[On, Using]]):
        super().__init__()
        self._from_item, self._join_condition = args
class From(SQL): # from (interpolated)
    _source: Union[Table, "Query"] # only 1 FromClause is supported right now

    def _serialize_(self) -> List[Token]:
        return [Token("FROM", C.KEYWORD)] + self._table_or_query(self._source)

    def __init__(self, arg: Union[str, Table, "Query"]):
        super().__init__()
        if isinstance(arg, str):
            self._source = Table(arg)
        else:
            self._source = arg
class Select(SQL):
    _nt1: Optional[Union[Struct, Value]]
    _nt2: Optional[SelectMode]
    _cols: List[Col] # this is provisional

    def _serialize_(self) -> List[Token]:
        return [Token("SELECT", C.KEYWORD)] + self._sep([col._serialize() for col in self._cols], COMMA)

    def __init__(self, cols: Union[List[Col], str]):
        super().__init__()
        if isinstance(cols, List):
            self._cols = cols
        elif isinstance(cols, str):
            self._cols = [Col(cols)]

class Except(SQL):
    _cols: List[Col]

    def _serialize(self) -> List[Token]:
        return [Token("EXCEPT", C.KEYWORD), LP] + self._sep([col._serialize() for col in self._cols], COMMA) + [RP]

    def __init__(self, cols: List[Col]):
        super().__init__()
        self._cols = cols

class With(SQL): # with (interpolated)
    _queries: List["Query"]

    def _serialize_(self) -> List[Token]:
        return [Token("WITH", C.KEYWORD)] + self._sep([cte._serialize() for cte in self._queries], COMMA)

    def __init__(self, queries: List["Query"]):
        super().__init__()
        for query in queries:
            assert not (query._pre_alias is None and query._post_alias is None and query._raw is None), "Each query in a with clause needs an alias"
            if query._post_alias:
                query._pre_alias = query._post_alias
                query._post_alias = None
        self._queries = queries


# TODO document Col and Join CFG changes
class NewTable(SQL):
    _query: "Query"
    _table: Table
    _method: Token
    _option: Token

    def AS(self, alias: Union[Table, str]) -> None:
        if isinstance(alias, str):
            self._table = Table(alias)
        else:
            self._table = alias
        return self

    def _serialize(self) -> List[Token]:
        result = [self._method] + self._table._serialize()
        if self._option:
            result += [self._option]
        result += [AS, LP] + self._query._serialize() + [RP]
        return result

    def __init__(
        self,
        METHOD:Token,
        AS:"Query",
        NAME:Union[str, Table],
        OPTION:Optional[Token] = None
    ):
        super().__init__()

        if METHOD in (CREATE_OR_REPLACE, CREATE_OR_REPLACE_TEMP) and OPTION==IF_NOT_EXISTS:
            raise Exception(f"{METHOD.data} cannot appear with {OPTION.data}")

        # _method
        self._method = METHOD
        # _query
        self._query = AS
        # _table
        if isinstance(NAME, str):
            self._table = Table(NAME)
        else:
            self._table = NAME
        # _option
        self._option = OPTION

class Query(SQL): # query_expr
    _with: Optional[With]
    _operation: Union[Select, "Query", SetOperation]
    _except: Optional[List[Col]]
    _from: From
    _join: Optional[Join]
    _where: Optional[Where]
    _group_by: Optional[GroupBy]
    _having: Optional[Having]
    _qualify: Optional[Qualify]
    _order_by: Optional[OrderBys]
    _limit: Optional[Limit]
    _pre_alias: Optional[str]
    _post_alias: Optional[str]

    # syntactic sugar for changing or setting alias
    def AS(self, alias: str) -> None:
        self._post_alias = alias
        return self

    def _serialize_(self) -> List[Token]:
        query = self._chain([
            self._with,
            self._operation,
            self._except,
            self._from,
            self._join,
            self._where,
            self._group_by,
            self._having,
            self._qualify,
            self._order_by,
            self._limit
        ])
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
        EXCEPT: Union[str, List[Col], Col, Except] = None,
        # these all technically belong to select
        FROM: Optional[Union[str, Table, "Query", From]] = None,
        JOIN: Optional[Tuple[Union[Table, "Query"], Union[On, Using]]] = None, # will be supported with something like the signature below in a (near-)future release
        # JOIN: Optional[Union[str, Tuple[Union[str, "Query"], JoinCondition], Join]] = None,
        WHERE: Optional[Where] = None,
        GROUP_BY: Optional[Union[Col, GroupBy]] = None,
        HAVING: Optional[Having] = None,
        QUALIFY: Optional[Qualify] = None,
        WINDOW: Optional[Window] = None,
        # these two actually belong to a query in the grammar
        ORDER_BY: Optional[Union[OrderBy, List[OrderBy], List[Col], Col, Tuple[Col, Token], List[Tuple[Col, Token]]]] = None, # TODO: need to cover Exp and (Exp, Token)
        LIMIT: Optional[Union[Limit, int]] = None,
        AS: Optional[str] = None,
        # the rest of the join types go here to avoid cluttering the tooltip
    ):
        super().__init__()
        # _with
        if WITH is None:
            self._with = None
        elif isinstance(WITH, List):
            self._with = With(WITH)
        elif isinstance(WITH, With):
            self._with = WITH
        
        # _operation (only select for now)
        if isinstance(SELECT, str) or isinstance(SELECT, List):
            self._operation = Select(SELECT)
        elif isinstance(SELECT, Select):
            self._operation = SELECT

        # _except
        # Union[str, List[Col], Col, Except]
        if EXCEPT is None:
            self._except = None
        elif isinstance(EXCEPT, Except):
            self._except = EXCEPT
        elif isinstance(EXCEPT, str):
            self._except = Except([Col(Except)])
        else:
            self._except = Except(EXCEPT)

        # _from
        if FROM is None:
            self._from = From(Table.raw(""))
        elif isinstance(FROM, Table) or isinstance(FROM, Query) or isinstance(FROM, str):
            self._from = From(FROM)
        elif isinstance(FROM, From):
            self._from = FROM

        # _join
        if JOIN is None:
            self._join = None
        else:
            self._join = Join(JOIN)

        # _select args
        self._where = WHERE

        # _group_by
        #Optional[Union[Col, GroupBy]]
        if GROUP_BY is None:
            self._group_by = None
        elif isinstance(GROUP_BY, Col):
            self._group_by = GroupBy(GROUP_BY)
        else:
            self._group_by = GROUP_BY
       
        self._having = HAVING
        self._qualify = QUALIFY
        self._window = WINDOW

        # aliases
        self._pre_alias = None
        self._post_alias = AS

        # _order_by
        # Optional[Union[, List[OrderBy], List[Col], List[Tuple[Col, Token]]]]
        if ORDER_BY is None:
            self._order_by = None
        elif isinstance(ORDER_BY, OrderBy):
            self._order_by = OrderBys([ORDER_BY])
        elif isinstance(ORDER_BY, Col):
            self._order_by = OrderBys([OrderBy(ORDER_BY)])
        elif isinstance(ORDER_BY, Tuple):
            self._order_by = OrderBys([OrderBy(col=ORDER_BY[0], order=ORDER_BY[1])])
        else :
            if len(ORDER_BY) == 0:
                self._order_by = None
            else:
                if isinstance(ORDER_BY[0], OrderBy):
                    self._order_by = OrderBys(ORDER_BY)
                elif isinstance(ORDER_BY[0], Col):
                    self._order_by = OrderBys([OrderBy[c] for c in ORDER_BY])
                else:
                    self._order_by = OrderBys([OrderBy(col=c[0], order=c[1]) for c in ORDER_BY])
        
        # _limit
        if LIMIT is None:
            self._limit = None
        elif isinstance(LIMIT, Limit):
            self._limit = LIMIT
        else:
            self._limit = Limit(LIMIT)

#TODO
# isinstance checks for newly supported parameters
# tests for new parameters
# partitions
# search in report templates and scopes and exports queries