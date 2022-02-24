import classy from 'classy-decorator'

class GrammarElement {}

@classy()
class Type { 
    constructor(type, basic = false) {
        this.type = type
        this.basic = basic
    }
}

const string = Type('string', true)
const number = Type('number', true)
const array = Type('array', true)
const boolean = Type('boolean', true)

@classy()
class T extends GrammarElement {
    constructor(type, value = null) {
        this.type = type
        this.value = value
    }
}

@classy()
class REP extends GrammarElement { constructor(grammar_element) { this.ges = [grammar_element] } }

@classy()
class OPT extends GrammarElement { constructor(grammar_element) { this.ges = [grammar_element] } }

@classy()
class ONE extends GrammarElement { constructor(grammar_elements) { this.ges = grammar_elements } }

@classy()
class ALL extends GrammarElement { constructor(grammar_elements) { this.ges = grammar_elements } }

module.exports = {
    T, REP, OPT, ONE, ALL,
    Type,
    string, number, array, boolean
 }