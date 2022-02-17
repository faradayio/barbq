// WORD -> Token("WORD", C.KEYWORD)
const fs = require('fs')
let keywords = fs.readFileSync('./config/keywords.txt', 'utf8')
let script = `
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
${keywords.split('\n').map(kw => `Token("${kw}", C.KEYWORD)`).join('\n')}
`
console.log(script)