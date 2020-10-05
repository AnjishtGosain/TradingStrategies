import pandas

from abc import ABCMeta, abstractmethod
from Common.DataStructures.PortfolioPerformance import PortfolioPerformance


class IPortfolio(object):
    '''
    An abstract base class representing a portfolio of positions (including both instruments and cash), 
    determined on the basis of a set of signals provided by an ITradingStrategy.
    '''

    __metaclass__ = ABCMeta

    @abstractmethod
    def CalculatePortfolioReturns(
            self, returnsDF: pandas.DataFrame, executionCostRate: float) -> PortfolioPerformance:
        '''
        Provides the logic to determine how the portfolio positions are allocated on the basis of forecasting
        signals.
        '''
        raise NotImplementedError("Should implement RebalancePortfolio()!")

    @abstractmethod
    def RebalancePortfolio(self, previousPortfolioWeights: pandas.DataFrame,
                           currentPortfolioSignals: pandas.DataFrame):
        '''
        Provides the logic to determine how the portfolio positions are allocated on the basis of forecasting 
        signals.
        '''
        raise NotImplementedError("Should implement RebalancePortfolio()!")

    @abstractmethod
    def BacktestPortfolio(self):
        '''
        Provides the logic to generate the trading orders and subsequent equity curve (i.e. growth of total 
        equity), as a sum of holdings and cash, and the bar-period returns associated with this curve based on 
        the 'positions' DataFrame. Produces a portfolio object that can be examined by other classes/functions.
        '''
        raise NotImplementedError("Should implement BacktestPortfolio()!")
