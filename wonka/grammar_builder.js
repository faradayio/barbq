import classy from 'classy-decorator'

class GrammarElement {}

@classy()
class Type { 
    constructor(type) {
        this.type = type
        
    }
}
@classy()
class T { constructor(t) { this.token = token } }

@classy()
class N { constructor(custom_type) { this.type = custom_type }}

@classy()
class REP { constructor(cog) { this.cog = cog } }

@classy()
class OPT { constructor(cog) { this.cog = cog } }

@classy()
class ONE { constructor(cogs) { this.cogs = cogs } }

@classy()
class ALL { constructor(cogs) { this.cogs = cogs } }

class C { constructor(custom_type) { this.type = custom_type} }

const str = 

module.exports = { T, N, REP, OPT, ONE, ALL }