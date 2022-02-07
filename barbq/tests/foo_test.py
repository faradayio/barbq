from unittest import TestCase
from barbq.query import (
    CREATE,
    CREATE_OR_REPLACE_TEMP,
    Col,
    Exp,
    GroupBy,
    NewTable,
    On,
    OrderBy,
    Query,
    Table,
    Using,
    Where,
    DESC,
    ASC,
    Case,
    NULL
)
class TestQuery(TestCase):
    def test_minimal_query(self):
        basic_query = Query(
            SELECT=[
                Col("grannies.name"),
                Col("specialty"),
                Col("grannies.hobby"),
            ],
            FROM=Table("acceptance-237317.kirby.grandmothers", AS="grannies"),
        )
        print(basic_query.render())
        expected = """SELECT `grannies`.`name` , `specialty` , `grannies`.`hobby` FROM `acceptance-237317`.`kirby`.`grandmothers` AS `grannies`"""
        assert basic_query.render() == expected

    def test_simple_cte(self):
        grandmothers = Table("acceptance-237317.kirby.grandmothers").AS("grannies")
        basic_cte = Query(
            WITH=[
                Query(
                    SELECT=[
                        Col("specialty"),
                        Col.raw(f"""COUNT({Col("names")})""")
                    ],
                    FROM=grandmothers,
                    GROUP_BY=Col("specialty"),
                    AS="summary_specialties"
                )
            ],
            SELECT=[Col.raw("*")],
            FROM=Table("summary_specialties")
        )

    def test_omniquery(self): # integration test
        ref_scores = Table("acceptance-237317.kirby.ref_scores")
        grandmothers = Table("acceptance-237317.kirby.grandmothers").AS("grannies")
        omniquery = Query(
            WITH=[
                Query(
                    WITH=[
                        Query(
                            SELECT=[
                                Col("name"),
                                Col.raw(
                                    "CAST(hilda AS float64) + CAST(cookies AS float64) + CAST(knitting AS float64) AS hilda_score"
                                ),
                                Col.raw(
                                    "CAST(mary AS float64) + CAST(bread as float64) + CAST(hockey AS float64) AS mary_score"
                                ),
                            ],
                            FROM=grandmothers,
                            AS="summary_scores",
                        )
                    ],
                    SELECT=[
                        Col("grannies.name", AS="name"),
                        Col("hilda_score"),
                        Col("mary_score"),
                    ],
                    FROM=grandmothers,
                    JOIN=(Table("summary_scores"), On.raw("ON summary_scores.name=grannies.name")),
                    AS="scored_grandmas",
                ),
                Query.raw(
                    f"combos AS (SELECT * FROM scored_grandmas CROSS JOIN {ref_scores.render()})"
                ),
            ],
            SELECT=[
                Col("brand"),
                Col("name", AS="granny"),
                Col.raw("relevance_score * mary_score AS score"),
            ],
            FROM=Table("combos"),
            WHERE=Where.raw("""WHERE granny='mary' -- for brands that care about similarity to mary, show how much they are interested in each of our grandmothers"""),
        )
        print(omniquery.render())
        expected = """WITH `scored_grandmas` AS ( WITH `summary_scores` AS ( SELECT `name` , CAST(hilda AS float64) + CAST(cookies AS float64) + CAST(knitting AS float64) AS hilda_score , CAST(mary AS float64) + CAST(bread as float64) + CAST(hockey AS float64) AS mary_score FROM `acceptance-237317`.`kirby`.`grandmothers` AS `grannies` ) SELECT `grannies`.`name` AS `name` , `hilda_score` , `mary_score` FROM `acceptance-237317`.`kirby`.`grandmothers` AS `grannies` JOIN `summary_scores` ON summary_scores.name=grannies.name ) , combos AS (SELECT * FROM scored_grandmas CROSS JOIN `acceptance-237317`.`kirby`.`ref_scores`) SELECT `brand` , `name` AS `granny` , relevance_score * mary_score AS score FROM `combos` WHERE granny='mary' -- for brands that care about similarity to mary, show how much they are interested in each of our grandmothers"""
        print(expected)
        assert omniquery.render() == expected

    def test_exp(self):
        assert Col(Exp("APPROX_QUANTILES(column, 100)")).render() == "APPROX_QUANTILES(column, 100)"

    def test_interpolation(self):
        assert f"{Col('column')}" == "`column`"
        assert f"{Col('my_project.my_dataset.my_column')}" == "`my_project`.`my_dataset`.`my_column`"

    def test_initialize_from_using_str(self):
        pass

    def test_using(self):
        grandmothers = Table("acceptance-237317.kirby.grandmothers").AS("grannies")
        baking_goods = Table("acceptance-237317.kirby.baking")

        using_query = Query(
            SELECT=[
                Col("first_name"),
                Col("last_name"),
                Col.raw("item AS signature_baking")
            ],
            FROM=grandmothers,
            JOIN=(baking_goods,Using(Col("dish_id")))
        )
        print(using_query.render())
        expected = """SELECT `first_name` , `last_name` , item AS signature_baking FROM `acceptance-237317`.`kirby`.`grandmothers` AS `grannies` JOIN `acceptance-237317`.`kirby`.`baking` USING `dish_id`"""
        print(expected)
        assert using_query.render() == expected

    def test_on(self):
        grandmothers = Table("acceptance-237317.kirby.grandmothers").AS("grannies")
        baking_goods = Table("acceptance-237317.kirby.baking"). AS("baking")

        on_query = Query(
            SELECT=[
                Col("first_name"),
                Col("last_name"),
                Col.raw("item AS signature_baking")
            ],
            FROM=grandmothers,
            JOIN=(baking_goods,On(Col("grannies.baki_id"), Col("baking.id")))
        )
        print(on_query.render())
        expected = """SELECT `first_name` , `last_name` , item AS signature_baking FROM `acceptance-237317`.`kirby`.`grandmothers` AS `grannies` JOIN `acceptance-237317`.`kirby`.`baking` AS `baking` ON `grannies`.`baki_id` = `baking`.`id`"""
        print(expected)
        assert on_query.render() == expected

    def test_where(self):
        grandmothers = Table("acceptance-237317.kirby.grandmothers").AS("grannies")
        where_query = Query(
            SELECT=[
                Col("name"),
                Col.raw(
                    "CAST(chololate AS float64) + CAST(flour AS float64) + CAST(knitting AS float64) AS baking_score"
                )
            ],
            FROM=grandmothers,
            AS="summary_scores",
            WHERE=Where.raw("""WHERE granny='mary' OR age > 65"""),
        )
        print(where_query.render())
        expected = """SELECT `name` , CAST(chololate AS float64) + CAST(flour AS float64) + CAST(knitting AS float64) AS baking_score FROM `acceptance-237317`.`kirby`.`grandmothers` AS `grannies` WHERE granny='mary' OR age > 65 AS `summary_scores`"""
        print(expected)
        assert where_query.render() == expected
        
    def test_group_by(self):
        grandmothers = Table("acceptance-237317.kirby.grandmothers").AS("grannies")
        group_query = Query(
            SELECT=[
                Col.raw("DIV(age, 5) * 5 AS age_bin"),
                Col.raw("COUNT(*) AS pop_count")
            ],
            FROM=grandmothers,
            GROUP_BY=Col.raw("COUNT(*)")
        )
        print(group_query.render())
        expected = """SELECT DIV(age, 5) * 5 AS age_bin , COUNT(*) AS pop_count FROM `acceptance-237317`.`kirby`.`grandmothers` AS `grannies` COUNT(*)"""
        print(expected)
        assert group_query.render() == expected

    def test_integer_literal_token(self):
        # for not this is covered by test_limit
        pass

    def test_list_int_literal_token(self):
        pass

    def test_list_str_literal_token(self):
        pass

    def test_limit(self):
        grandmothers = Table("acceptance-237317.kirby.grandmothers")

        limit_query = Query(
            SELECT=[
                Col.raw("*")
            ],
            FROM=grandmothers,
            AS="sampled_grannies",
            LIMIT=100
        )
        print(limit_query.render())
        expected = """SELECT * FROM `acceptance-237317`.`kirby`.`grandmothers` AS `grannies` LIMIT 100 AS `sampled_grannies`"""
        print(expected)
        assert limit_query.render() == expected

    def test_star_col(self):
        grandmothers = Table("acceptance-237317.kirby.grandmothers")

        limit_query = Query(
            FROM=grandmothers,
            AS="sampled_grannies",
            LIMIT=100
        )

        print(limit_query.render())
        expected = """SELECT * FROM `acceptance-237317`.`kirby`.`grandmothers` LIMIT 100 AS `sampled_grannies`"""
        print(expected)
        assert limit_query.render() == expected

        limit_query_2 = Query(
            SELECT="*",
            FROM=grandmothers,
            AS="sampled_grannies",
            LIMIT=100
        )

        print(limit_query_2.render())
        expected = """SELECT * FROM `acceptance-237317`.`kirby`.`grandmothers` LIMIT 100 AS `sampled_grannies`"""
        assert limit_query_2.render() == expected

    def test_order_by(self):
        grandmothers = Table("acceptance-237317.kirby.grandmothers")

        order_query = Query(
            FROM=grandmothers,
            ORDER_BY=(Col("name"), DESC)
        )

        print(order_query.render())
        expected = """SELECT * FROM `acceptance-237317`.`kirby`.`grandmothers` ORDER BY `name` DESC"""
        print(expected)
        assert order_query.render() == expected

        order_query_2 = Query(
            SELECT="*",
            FROM=grandmothers,
            ORDER_BY=[
                (Col("age"), DESC),
                (Col("last_name"), ASC),
                (Col("last_name"), ASC),
            ],
            LIMIT=100
        )

        print(order_query_2.render())
        expected = """SELECT * FROM `acceptance-237317`.`kirby`.`grandmothers` ORDER BY `age` DESC , `last_name` ASC , `last_name` ASC LIMIT 100"""
        assert order_query_2.render() == expected

    def test_order_by_with_sort(self):
        grandmothers = Table("acceptance-237317.kirby.grandmothers").AS("grannies")
        order_w_sort_query = Query(
            SELECT=[
                Col("first_name"),
                Col("last_name"),
                Col("age")
            ],
            FROM=grandmothers,
            ORDER_BY=[
                (Col("age"), ASC),
                (Col("last_name"), DESC)
            ]
        )
        print(order_w_sort_query.render())
        expected = """SELECT `first_name` , `last_name` , `age` FROM `acceptance-237317`.`kirby`.`grandmothers` AS `grannies` ORDER BY `age` ASC , `last_name` DESC"""
        print(expected)
        assert order_w_sort_query.render() == expected

    def test_boolean_and(self):
        pass

    def test_boolean_or(self):
        pass

    def test_chained_bool(self):
        pass

    def test_except(self):
        grandmothers = Table("acceptance-237317.kirby.grandmothers")

        except_query = Query(
            SELECT=[
                Col.raw("*")
            ],
            EXCEPT=[Col("name"), Col("date_of_birth")],
            FROM=grandmothers,
            AS="anonymized_grannies",
            LIMIT=100
        )
        print(except_query.render())
        expected = """SELECT * EXCEPT ( `name` , `date_of_birth` ) FROM `acceptance-237317`.`kirby`.`grandmothers` AS `grannies` LIMIT 100 AS `anonymized_grannies`"""
        print(expected)
        assert except_query.render() == expected

    def test_new_table(self):
        new_table = Table("currated_scores")
        new_table_query = NewTable(
            METHOD=CREATE_OR_REPLACE_TEMP,
            AS=Query(
                SELECT=[
                    Col("scores"),
                    Col.raw("COUNT(*) AS total")
                ],
                FROM=Table("scores_table"),
                GROUP_BY=Col("scores"),
                ORDER_BY=OrderBy(Col("total"), DESC)
            ),
            NAME=new_table
        )

        print(new_table_query.render())
        expected = """CREATE OR REPLACE TEMP `currated_scores` AS ( SELECT `scores` , COUNT(*) AS total FROM `scores_table` GROUP BY `scores` ORDER BY `total` DESC )"""
        assert new_table_query.render() == expected

    def test_case(self):
        grandmothers = Table("acceptance-237317.kirby.grandmothers")

        case_query = Query(
            SELECT=[
                Col("first_name"),
                Col("last_name"),
                Col("investment_resources"),
                Case(
                    CASE=[
                        Exp("investment_resources = 'No Investment' THEN 1"),
                        Exp("investment_resources = 'Less than $4,999' THEN 2"),
                        Exp("investment_resources = '$5,000 - $49,999' THEN 3"),
                        Exp("investment_resources = '$50,000 - $149,999' THEN 4"),
                        Exp("investment_resources = '$150,000 - $199,999' THEN 5"),
                        Exp("investment_resources = '$200,000 - $249,999' THEN 6"),
                        Exp("investment_resources = '$250,000 - $499,999' THEN 7"),
                        Exp("investment_resources = '$500,000 or more' THEN 8")
                    ],
                    ELSE=Exp("NULL")
                )

            ],
            FROM=grandmothers
        )
        print(case_query.render())
        expected = """SELECT `first_name` , `last_name` , `investment_resources` , CASE WHEN investment_resources = 'No Investment' THEN 1 WHEN investment_resources = 'Less than $4,999' THEN 2 WHEN investment_resources = '$5,000 - $49,999' THEN 3 WHEN investment_resources = '$50,000 - $149,999' THEN 4 WHEN investment_resources = '$150,000 - $199,999' THEN 5 WHEN investment_resources = '$200,000 - $249,999' THEN 6 WHEN investment_resources = '$250,000 - $499,999' THEN 7 WHEN investment_resources = '$500,000 or more' THEN 8 ELSE NULL END FROM `acceptance-237317`.`kirby`.`grandmothers`"""
        print(expected)
        assert case_query.render() == expected