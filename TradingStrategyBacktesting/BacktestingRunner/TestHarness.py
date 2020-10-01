import numpy
import pandas

from BacktestingEngine.BacktestingEngine import BacktestingEngine 
from Common.Enumerations.FactorName import FactorName 
from Common.Enumerations.ReturnType import ReturnType 
from TradingStrategies.TradingStrategyName import TradingStrategyName
from PortfolioConstruction.PortfolioConstructionName import PortfolioConstructionName

if __name__ == "__main__":
    inputCachePathStr = "C:/Users/anjis/Documents/AnjishtGosain_ChallengerSolution" 
    filenameStr = "dataset.csv"
    backtestingEngine = BacktestingEngine(inputCachePathStr, filenameStr)
    backtestingEngine.BacktestTradingStrategy(TradingStrategyName.LongBestShortWorst, PortfolioConstructionName.DollarNeutralEqualWeightPortfolio, 
                                              FactorName.Factor1, 0.2, 0.1)
    blah = 0;
