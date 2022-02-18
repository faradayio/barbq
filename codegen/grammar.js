bigquery = {
    'QUERY':  ALL(
        OPT('WITH'),
        ONE(
            'SELECT',
            ALL('(', 'Query', ')'),
            ALL(
                'QUERY',
                ONE(
                    ALL('UNION', ONE('ALL', 'DISTINCT')),
                    ALL('INTERSECT', 'DISTINCT'),
                    ALL('EXCEPT', 'DISTINCT')
                ),
                'QUERY'
            )
        ),
        OPT('ORDERBY'),
        OPT('LIMIT')
    ),
    'ORDERBY': REP(ALL(
        'EXP',
        OPT(ONE('ASC', 'DESC')),
        OPT('NULLS', ONE('FIRST', 'LAST'))
    )),
    'LIMIT': ALL('EXP', 'OFFSET'),
    'OFFSET': 'EXP'
}