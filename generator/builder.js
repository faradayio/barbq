const { generate_classes } = require('../wonka/class_generator')
const { T, OPT, REP, ALL, ONE } = require('../wonka/grammar_builder')

bigquery = {
    'QUERY':  ALL(
        OPT(T('WITH')),
        ONE(
            T('SELECT'),
            ALL(T('QUERY')),
            ALL(
                T('QUERY'),
                ONE(
                    ALL(T('UNION'), ONE(T('ALL'), T('DISTINCT'))),
                    ALL(T('INTERSECT'), T('DISTINCT')),
                    ALL(T('EXCEPT'), T('DISTINCT'))
                ),
                T('QUERY')
            )
        ),
        OPT(T('ORDERBY')),
        OPT(T('LIMIT'))
    ),
    'ORDERBY': ALL(
        T('EXP'),
        OPT(ONE(T('ASC'), T('DESC'))),
        OPT(ALL(T('NULLS'), ONE(T('FIRST'), T('LAST'))))
    ),
    'LIMIT': ALL(T('EXP'), T('OFFSET')),
    'OFFSET': ALL(T('EXP')),
    'WITH': ALL(),
    'EXP': ALL(),
    'SELECT': ALL(),
    'UNION': ALL(),
    'ALL': ALL(),
    'DISTINCT': ALL(),
    'INTERSECT': ALL(),
    'EXCEPT': ALL(),
    'ASC': ALL(),
    'DESC': ALL(),
    'NULLS': ALL(),
    'FIRST': ALL(),
    'LAST': ALL(),
}

generate_classes('./codegen/preamble.py', bigquery, './codegen/generated.py', 'python')