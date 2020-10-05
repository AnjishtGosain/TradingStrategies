import numpy
import pandas

from BacktestingEngine.BacktestingEngine import BacktestingEngine
from Common.Enumerations.FactorName import FactorName
from Common.Enumerations.ReturnType import ReturnType
from TradingStrategies.TradingStrategyName import TradingStrategyName
from PortfolioConstruction.PortfolioConstructionName import PortfolioConstructionName

if __name__ == "__main__":
    inputCachePathStr = "."
    filenameStr = "dataset.csv"
    backtestingEngine = BacktestingEngine(
        inputCachePathStr=inputCachePathStr, inputDataFilenameStr=filenameStr)

    portfolioPerformance = backtestingEngine.BacktestTradingStrategy(
        tradingStrategyName=TradingStrategyName.LongBestShortWorst,
        portfolioConstructionName=PortfolioConstructionName.DollarNeutralEqualWeightPortfolio,
        factorName=FactorName.Factor2, percentile=0.2, executionCostRate=0.1)
