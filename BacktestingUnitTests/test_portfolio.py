import pandas as pd
import unittest
import pandas.testing as pd_testing

from PortfolioConstruction.DollarNeutralEqualWeightPortfolio import DollarNeutralEqualWeightPortfolio


class TestPortfolioConstruction(unittest.TestCase):
    def assertDataframeEqual(self, a, b, msg):
        try:
            pd_testing.assert_frame_equal(a, b)
        except AssertionError as e:
            raise self.failureException(msg) from e

    def setUp(self):
        self.addTypeEqualityFunc(pd.DataFrame, self.assertDataframeEqual)

    def test_portfolio_construction(self):

        # Inputs for portfolio construction
        # =================================
        previousPortfolioWeightsDF = pd.DataFrame({
            'A': 0.336035009195627,
            'B': -1.013382533016710,
            'C': 0.336407140988756,
            'D': 0.335493726587439
        }, index=[0])

        currentPortfolioSignalsDF = pd.DataFrame({
            'A': -1.0,
            'B': 0.0,
            'C': 1.0,
            'D': 0.0
        }, index=[0])

        portfolio = DollarNeutralEqualWeightPortfolio(previousPortfolioWeightsDF, currentPortfolioSignalsDF)

        # Theoretical outputs from portfolio construction
        # ===============================================

        theoreticalChangeInPortfolioWeightsDF = pd.DataFrame({
            0: -1.346694214089890,
            1: 1.013382533016710,
            2: 0.674252063905511,
            3: -0.335493726587439
        }, index=[0])

        theoreticalPortfolioWeightsDF = pd.DataFrame({
            'A': -1.01065920489427,
            'B': 0.00000000000000,
            'C': 1.01065920489427,
            'D': 0.00000000000000
        }, index=[0])

        self.assertEqual(theoreticalChangeInPortfolioWeightsDF, portfolio.ChangeInPortfolioWeightsDF)
        self.assertEqual(theoreticalPortfolioWeightsDF, portfolio.PortfolioWeightsDF)

    def test_portfolio_returns(self):

        # Inputs for portfolio construction
        # =================================
        previousPortfolioWeightsDF = pd.DataFrame({
            'A': 0.336035009195627,
            'B': -1.013382533016710,
            'C': 0.336407140988756,
            'D': 0.335493726587439
        },
            index=[0])

        currentPortfolioSignalsDF = pd.DataFrame({
            'A': -1.0,
            'B': 0.0,
            'C': 1.0,
            'D': 0.0
        },
            index=[0])

        portfolio = DollarNeutralEqualWeightPortfolio(previousPortfolioWeightsDF, currentPortfolioSignalsDF)

        returnsDF = pd.DataFrame({
            'A': 0.01,
            'B': 0.013,
            'C': -0.067,
            'D': -0.3
        },
            index=[0])

        portfolioReturn = portfolio.CalculatePortfolioReturns(returnsDF, 0.0)
        self.assertAlmostEqual(portfolioReturn.LongPortfolioReturn, -0.067)
        self.assertAlmostEqual(portfolioReturn.ShortPortfolioReturn, -0.01)
        self.assertAlmostEqual(portfolioReturn.LongShortPortfolioReturn, -0.077)
        # portfolioReturn = portfolio.CalculatePortfolioReturns(returnsDF, 0.2)
        # assert(portfolioReturn.LongPortfolioReturn, -0.4004281745301176)
        # assert(portfolioReturn.ShortPortfolioReturn, -0.3434281745301177)
        # assert(portfolioReturn.LongShortPortfolioReturn, 0.25614365093976466)


if __name__ == '__main__':
    unittest.main()
