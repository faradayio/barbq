  There are three types of _private_data fields:

type                        CFG equiv
SubClass(SQL)               non-terminal
str                         custom terminal
Token                       keyword terminal from a set
generated by _serialize_    ()


then we apply a formula based on the CFG specification

type                                                                    CFG equiv
Optional[Type]                                                          [ symbol ]
Union[Type1, Type2]                                                     symbol1 | symbol2
Union[Type, List[Type]]                                                 [, …]
logical parenthesis; sets the nesting structure of the complex types    {}
_serialize_ knows to insert LP RP Tokens                                ()

key barbq object / conceptual role

with / list of queries

query / top level relation object

table / identifier for a table

col / identifier for a col, or expression col

relation / a query or a table

aliasable / superclass of table, col, query

join / 2 relations -> 1 relation

from / list of relations

select / list of columns
