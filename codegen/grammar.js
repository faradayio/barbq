bigquery = {
    'QUERY':  ALL(
        OPT('With'),
        ONE(
            'Select',
            ALL('(', 'Query', ')'),
            ALL(
                'Query',
                ONE(
                    ALL('UNION', ONE('ALL', 'DISTINCT')),
                    ALL('INTERSECT', 'DISTINCT'),
                    ALL('EXCEPT', 'DISTINCT')
                ),
                'Query'
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
    'LIMIT': ALL('EXP', 'OFFSET')
}