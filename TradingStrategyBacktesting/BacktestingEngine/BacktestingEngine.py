import pandas

from pathlib import Path

from Common.Enumerations.CacheType import CacheType
from BacktestingEngine.DataProvider import DataProvider
from PortfolioConstruction.PortfolioConstructionName import PortfolioConstructionName
from TradingStrategies.TradingStrategyName import TradingStrategyName
from TradingStrategies.LongBestShortWorst import LongBestShortWorst
from PortfolioConstruction.DollarNeutralEqualWeightPortfolio import DollarNeutralEqualWeightPortfolio
from Common.Enumerations.FactorName import FactorName 
from Common.Enumerations.ReturnType import ReturnType 

class BacktestingEngine(object):
    '''
    This class runs the backtesting for a given set of inputs 
    '''

    def __init__(self, inputCachePathStr: str, inputDataFilenameStr : str, cacheType = CacheType.Csv):
        self.InputCachPath = Path(inputCachePathStr)
        self.InputDataFileName = inputDataFilenameStr
        self.CacheType = cacheType
        self.Data = pandas.DataFrame() 

    def BacktestTradingStrategy(self, tradingStrategyName : TradingStrategyName, portfolioConstructionName : PortfolioConstructionName, 
                                factorName : FactorName, percentile : float, executionCostRate = 0.0):
        '''
        This function runs the historical backtest for the specified trading strategy, portfolio construction method, and factor name.
        '''

        self.Data = DataProvider.FilteredCachedLoad(self.InputCachPath, self.InputDataFileName) 

        if tradingStrategyName == TradingStrategyName.LongBestShortWorst and portfolioConstructionName == PortfolioConstructionName.DollarNeutralEqualWeightPortfolio:

            factorData = self.Data[factorName] 
            returnsData = self.Data[ReturnType.Mixed]
            portfolioPerformance = {}
            for i in range(len(factorData.index)):
                date = factorData.index[i]
                factorDataForDate = factorData.iloc[[i]]
                returnsDataForDate = returnsData.iloc[[i]] 
                signals = LongBestShortWorst.GenerateTradingSignals(factorDataForDate, percentile)
                portfolio = DollarNeutralEqualWeightPortfolio(previousPortfolioWeights, signals) 
                portfolioPerformance[date] = portfolio.CalculatePortfolioReturns(returnsDataForData, executionCostRate)
                previousPortfolioWeights = portfolio.PortfolioWeightsDF

        else:
            raise NotImplementedError("The requested combination of trading strategy and portfolio construction has not been implemented.")
