// WORD -> Token("WORD", C.KEYWORD)
const fs = require('fs')
// let keywords = fs.readFileSync('./config/keywords.txt', 'utf8')
// let script = `
// from typing import Any, List, Optional, Tuple, Union
// from enum import Enum, auto

// class C(Enum):
//     IDENTIFIER = auto()
//     LITERAL = auto()
//     KEYWORD = auto()
//     OPERATOR = auto()
//     SPECIAL = auto()
//     RAW = auto()

// class Token:
//     def __init__(self, data: Union[str, int], category: C):
//         assert isinstance(data, str) or category == C.LITERAL, "nonliteral tokens cannot have nonstring type"
//         self.data = data
//         self.category = category

// ${keywords.split('\n').map(kw => `Token("${kw}", C.KEYWORD)`).join('\n')}
// `
// console.log(script)

    
let minigrammar = fs.readFileSync('./codegen/config/minigrammar.txt', 'utf8')
const keywords = ['WITH', 'RECURSIVE', 'ORDER', 'BY', 'LIMIT', 'ASC', 'DESC', 'LIMIT', 'OFFSET', 'SELECT', 'STRUCT', 'VALUE', 'ALL', 'DISTINCT', 'EXCEPT', 'REPLACE', 'AS', 'FROM', 'GROUP', 'HAVING', 'QUALIFY', 'WINDOW', 'SYSTEM_TIME', 'OF', 'UNNEST', 'UNPIVOT', 'INCLUDE', 'NULLS', 'EXCLUDE', 'FOR', 'IN', 'CROSS', 'JOIN', 'INNER', 'FULL', 'OUTER', 'LEFT', 'RIGHT', 'ON', 'USING', 'FIRST', 'LAST', 'UNION', 'INTERSECT']
const dict = {
    '[': 'Optional[',
    ']': ']',
    '{': 'Union[',
    '|': ', ',
    '}': ']',
    'expression': 'Exp'
}
keywords.forEach(kw => {dict[kw] = 'Token'})

const typeMap = token => dict[token] ?? token

const tokens = minigrammar.split('\n').slice(1).map(line => line.split(' ').slice(4))

// field definitions
console.log(tokens.map(arr =>  [...arr, '\n']).map(arr => arr.map(typeMap)).flat().join(' '))

const string = `
class FUNC(Func):
    _args: List[Exp]

    def __serialize_(self):
        return []

    def __init__(self, ):
        pass

`

// constructor


// single unnamed arg
// pass-thru constructor in tuples

// keyword arg assume each line starts with a KW
// 

const string2 = `
def __init__(self, ):


`