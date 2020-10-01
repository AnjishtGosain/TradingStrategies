import pandas

from PortfolioConstruction.DollarNeutralEqualWeightPortfolio import DollarNeutralEqualWeightPortfolio

def TestPortfolioConstruction():

    # Inputs for portfolio construction
    # =================================
    previousPortfolioWeightsDF = pandas.DataFrame({'A' : 0.336035009195627, 'B' : -1.013382533016710, 'C' : 0.336407140988756, 'D' : 0.335493726587439},
                                                index = [0])
    currentPortfolioSignalsDF = pandas.DataFrame({'A' : -1.0, 'B' : 0.0, 'C' : 1.0, 'D' : 0.0}, index = [0])
    portfolio = DollarNeutralEqualWeightPortfolio(previousPortfolioWeightsDF, currentPortfolioSignalsDF)

    # Theoretical outputs from portfolio construction
    # ===============================================

    theoreticalChangeInPortfolioWeightsDF = pandas.DataFrame({'A' : -1.346694214089890, 'B' : 1.013382533016710, 'C' : 0.674252063905511, 
                                                              'D' : -0.335493726587439}, index = [0])
    theoreticalPortfolioWeightsDF = pandas.DataFrame({'A' : -1.01065920489427, 'B' : 0.00000000000000, 'C' : 1.01065920489427, 
                                                      'D' : 0.00000000000000}, index = [0])

    #print("ChangeInPortfolioWeights")
    #print(portfolio.ChangeInPortfolioWeightsDF)
    #print("TheoreticalChangeInPortfolioWeights")
    #print(theoreticalChangeInPortfolioWeightsDF)
    #print("PortfolioWeights")
    #print(portfolio.PortfolioWeightsDF)
    #print("TheoreticalPortfolioWeights")
    #print(theoreticalPortfolioWeightsDF)
    #print("TurnoverRatio")
    #print(portfolio.TurnoverRatio)
    #print("TheoreticalTurnoverRatio")
    #print(1.66714087265059)


def TestPortfolioReturnsCalculation():

    # Inputs for portfolio construction
    # =================================
    previousPortfolioWeightsDF = pandas.DataFrame({'A' : 0.336035009195627, 'B' : -1.013382533016710, 'C' : 0.336407140988756, 'D' : 0.335493726587439},
                                                index = [0])
    currentPortfolioSignalsDF = pandas.DataFrame({'A' : -1.0, 'B' : 0.0, 'C' : 1.0, 'D' : 0.0}, index = [0])
    portfolio = DollarNeutralEqualWeightPortfolio(previousPortfolioWeightsDF, currentPortfolioSignalsDF)

    returnsDF = pandas.DataFrame({'A' : 0.01, 'B' : 0.013, 'C' : -0.067, 'D' : -0.3}, index = [0])

    portfolioReturn = portfolio.CalculatePortfolioReturns(returnsDF, 0.2)
    assert(portfolioReturn.LongPortfolioReturn, -0.4004281745301176)
    assert(portfolioReturn.ShortPortfolioReturn, -0.3434281745301177)
    assert(portfolioReturn.PortfolioReturn, 0.25614365093976466)


if __name__ == '__main__':
    TestPortfolioConstruction()
    TestPortfolioReturnsCalculation()