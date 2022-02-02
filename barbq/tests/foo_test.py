from unittest import TestCase
from barbq.query import Col, Exp, On, OrderBy, Query, Table, Where
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

    def test_initialize_from_using_str(self):
        pass

    def test_using(self):
        pass

    def test_on(self):
        pass

    def test_where(self):
        pass

    def test_group_by(self):
        pass

    def test_integer_literal_token(self):
        pass

    def test_limit(self):
        pass

    def test_star_col(self):
        pass

    def test_order_by(self):
        pass

    def test_order_by_with_sort(self):
        pass