import pandas
import numpy

from PortfolioConstruction.IPortfolio import IPortfolio
from Common.DataStructures.PortfolioPerformance import PortfolioPerformance


class DollarNeutralEqualWeightPortfolio(IPortfolio):
    '''
    This class implements a dollar netural portfolio given a set of long/short signals from a trading 
    strategy. The securities are held in equal weighting.
    '''

    def __init__(self, previousPortfolioWeights: pandas.DataFrame, currentPortfolioSignals: pandas.DataFrame):
        self.TurnoverRatio = 0.0
        self.AbsoluteTotalWeight = 0.0
        self.PortfolioWeightsDF = pandas.DataFrame()
        self.ChangeInPortfolioWeightsDF = pandas.DataFrame()
        self.AbsoluteChangeInPortfolioWeights = 0.0
        self.PortfolioValue = 0.0
        self.RebalancePortfolio(previousPortfolioWeights, currentPortfolioSignals)

    def CalculatePortfolioReturns(
            self, returnsDF: pandas.DataFrame, executionCostRate=0.0) -> PortfolioPerformance:
        '''
        Given a set of security returns, calculate the portfolio returns. The problem sheet states that 
        execution costs are applied as a percentage of the absolute notional turned over at the rebalance. 
        Thus, the turnover must be calculated seperately to the execution costs. In essence the trading 
        strategy is assigned captial at the start of the backtest, with no further capital in flows or 
        outflows. The execution costs are seperate from these.

        executionCostRate is expected as a number between 0.0 and 1.0.
        '''

        # Input validation
        # ================

        if executionCostRate < 0.0:
            raise ValueError(f"The execution cost rate must be greater than or equal to zero.")

        if numpy.array_equal(self.PortfolioWeightsDF.columns, returnsDF.columns) == False:
            raise ValueError(f"The securities in the provided returns do not match those in the portfolio.")

        # Returns calculation
        # ===================

        # Long portfolio return : traditional return calculation of profit / initial portfolio value
        # ------------------------------------------------------------------------------------------

        longPortfolioWeightsDF = self.PortfolioWeightsDF.apply(
            lambda y: y.item() if y.item() > 0.0 else 0.0, axis=0, result_type='expand')
        longPortfolioValue_T1 = longPortfolioWeightsDF.dropna().values.sum()
        longPortfolioReturnsDF = longPortfolioWeightsDF * (1.0 + returnsDF)
        longPortfolioValue_T2 = numpy.nansum(longPortfolioReturnsDF.values)
        # due to dollar neutral assumption
        longPortfolioExecutionCosts = 0.5 * self.AbsoluteChangeInPortfolioWeights * executionCostRate
        longPortfolioProfit = (longPortfolioValue_T2 - longPortfolioValue_T1) - longPortfolioExecutionCosts
        longPortfolioReturn = longPortfolioProfit / longPortfolioValue_T1

        # Short portfolio : traditional return calculation of profit / initial (ignoring borrowing costs)
        # -----------------------------------------------------------------------------------------------

        # For this return the short portfolio is treated like a long portfolio, with a -1 for the return.
        # This is appropriate because a short portfolio can be reversed to generate a long portfolio.

        shortPortfolioWeightsDF = self.PortfolioWeightsDF.apply(
            lambda y: y.item() if y.item() < 0.0 else 0.0, axis=0, result_type='expand')
        shortPortfolioValue_T1 = shortPortfolioWeightsDF.dropna().values.sum()
        shortPortfolioReturnsDF = shortPortfolioWeightsDF * (1.0 + returnsDF)
        shortPortfolioValue_T2 = numpy.nansum(shortPortfolioReturnsDF.values)
        shortPortfolioExecutionCosts = longPortfolioExecutionCosts  # due to dollar neutral assumption
        # the short position values will be negative!
        shortPortfolioProfit = shortPortfolioValue_T2 - shortPortfolioValue_T1 - shortPortfolioExecutionCosts
        shortPortfolioReturn = shortPortfolioProfit / (-1.0 * shortPortfolioValue_T1)

        # Combined portfolio
        # ------------------

        # The inital capital for the combined portfolio will be zero because it is a dollar neutral portfolio.
        # Hence, a different approach is needed to calculate the return for the long-short portfolio. I
        # propose to use an accounting style return metric, which measures the change in the capital position
        # from the start of the period till the end.

        # Before doing any trading, the only capital we need (excluding transaction costs) is the value of the
        # long portfolio. Entering into the short portfolio generates an immediate cash profit, as well as a
        # future liability of the same size. Hence, its net accounting value is 0. At period end the short
        # portfolio will have a non-zero value after the liability is payed off.

        # At period end the account value of the long portfolio is equal to the value of the long securities
        # at that time, less transaction costs. Whereas, the account value of the short portfolio is the
        # portfolio value, less the inital short position loan, less transaction costs.

        portfolioReturn = (
            longPortfolioValue_T2 - longPortfolioExecutionCosts + shortPortfolioProfit) / longPortfolioValue_T1 - 1.0

        # Construct output
        # ----------------

        output = PortfolioPerformance(
            longShortPortfolioReturn=portfolioReturn,
            longPortfolioReturn=longPortfolioReturn,
            shortPortfolioReturn=shortPortfolioReturn,
            longShortTurnoverRatio=self.TurnoverRatio)
        return output

    def RebalancePortfolio(self, previousPortfolioWeightsDF: pandas.DataFrame,
                           currentPortfolioSignalsDF: pandas.DataFrame):
        '''
        Given the previous portfolio weights and the set of new signals, rebalance the portfolio. Both of these 
        inputs are assumed to be a single row.
        '''

        # Input validation
        # ================

        #numberOfRows = len(row.index)
        # if numberOfRows != 1:
        #    raise ValueError(f"This function requires a single row of data, rather than {numberOfRows} to be passed as an input.")

        # if numpy.array_equal(previousPortfolioWeightsDF.columns, currentPortfolioSignalsDF.columns) == False:
        #    raise ValueError(f"The previous portfolio weights and current porfolio signals do not correspond to the same set of securities.")

        # Rebalance the portfolio
        # =======================

        # Following portfolio rebalance, the absolute total weight for the current portfolio will be the same 
        # as that for the previous portfolio. This is because no new capital is being injected into the 
        # strategy. Moreover, since this portfolio is dollar neutral, the absolute total weight for the long 
        # positions will be the same as the absolute total weight for the short positions.

        currentLongSignalsCount = currentPortfolioSignalsDF.apply(
            lambda y: 1.0 if y.item() > 0.0 else 0.0, axis=0).dropna().values.sum()
        currentShortSignalsCount = currentPortfolioSignalsDF.apply(
            lambda y: 1.0 if y.item() < 0.0 else 0.0, axis=0).dropna().values.sum()

        previousAbsoluteTotalWeight = previousPortfolioWeightsDF.apply(lambda y: abs(y)).dropna().values.sum()
        if previousAbsoluteTotalWeight == 0.0:  # this is the first portfolio holding
            previousAbsoluteTotalWeight = 2.0

        self.AbsoluteTotalWeight = previousAbsoluteTotalWeight

        currentLongAbsoluteTotalWeight = self.AbsoluteTotalWeight / 2.0
        currentShortAbsoluteTotalWeight = self.AbsoluteTotalWeight / 2.0

        currentLongSignalsMultiplier = currentLongAbsoluteTotalWeight / currentLongSignalsCount
        currentShortSignalsMultiplier = currentShortAbsoluteTotalWeight / currentShortSignalsCount

        # Compute the new weights for the securities
        # Note that the weights are not rounded to account for the investment in whole securities. This is 
        # because no price data has been provided. One could potentially assume that each security has a price
        # of 1 cent, and round the weights accordingly.

        self.PortfolioWeightsDF = currentPortfolioSignalsDF.apply(
            lambda y: y * currentLongSignalsMultiplier
            if y.item() == 1.0 else y * currentShortSignalsMultiplier, result_type='expand')

        self.PortfolioValue = self.PortfolioWeightsDF.apply(lambda y: y.item(), axis=0).dropna().values.sum()

        # Calculate the turnover
        # ======================

        self.ChangeInPortfolioWeightsDF = pandas.DataFrame(
            [x1 - x2 for(x1, x2) in zip(self.PortfolioWeightsDF.values, previousPortfolioWeightsDF.values)])
        self.AbsoluteChangeInPortfolioWeights = self.ChangeInPortfolioWeightsDF.apply(
            lambda y: abs(y.item())).dropna().values.sum()
        self.TurnoverRatio = self.AbsoluteChangeInPortfolioWeights / previousAbsoluteTotalWeight
