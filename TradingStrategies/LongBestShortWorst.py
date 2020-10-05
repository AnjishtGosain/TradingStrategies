import numpy
import pandas

from TradingStrategies.ITradingStrategy import ITradingStrategy
from Common.Enumerations.FactorName import FactorName


class LongBestShortWorst(ITradingStrategy):
    '''
    Derives from ITradingStrategy to produce a set of signals that long the top x% and short the bottom x% 
    of securities on a given factor. Each security is then assigned an equal weighting, such that the 
    portfolio is dollar neutral.
    '''

    @staticmethod
    def GenerateTradingSignals(factorDataDF: pandas.DataFrame, percentile: float) -> pandas.DataFrame:
        '''
        Generates the trading signals based on the provided data set. Long and short securities are assigned 
        1 and -1 respectively, whilst securities with no holdings are assigned 0.

        Note that this class has been set up independently of the backtesting framework. Specifically, 
        signals are produced for each row of data, where each row is corresponds to a specific date and time. 
        For backtesting each row is historical, and for live trading it will be the 
        present.
        '''

        # Input validation
        # ================

        if percentile <= 0.0 or percentile > 0.5:
            raise ValueError(
                f"The percentile must be greater than 0.0, and less than or equal to 0.5. The value provided" +
                f" was {percentile}.")

        # Generate the signals
        # ====================

        signals = factorDataDF.apply(
            lambda x: LongBestShortWorst.__GenerateSingleRowTradingSignal(x, percentile),
            axis=1, result_type='expand')
        return signals

    @staticmethod
    def __GenerateSingleRowTradingSignal(row: pandas.DataFrame, percentile: float) -> list:
        '''
        For a single row of data, identify the largest x% and smallest y%.
        Note that for each row the number of the largest and smallest securities invested will vary depending 
        upon the number of securities with non null factor values.
        '''

        # Input validation
        # ================

        #numberOfRows = len(row.index)
        # if numberOfRows != 1:
        #    raise ValueError(f"This function requires a single row of data, rather than {numberOfRows} to be " + 
        #                       f"passed as an input.")

        # Apply trading rule
        # ==================

        # Sort the factor values to determine the nth largest and smallest values

        sortedFactorValues = sorted(row.dropna().values)  # remove the NaNs from the sorted list

        # Determine the number of securities which will be long.

        nonNullSecutitiesCount = len(sortedFactorValues)
        numberOfLongSecurities = int(nonNullSecutitiesCount * percentile)  # round down
        if numberOfLongSecurities == 0:
            raise ValueError(
                "The selected percentile is too low for the provided data. No trading signal will be generated.")

        shortSecuritiesBound = sortedFactorValues[numberOfLongSecurities - 1]
        longSecuritiesBound = sortedFactorValues[nonNullSecutitiesCount - numberOfLongSecurities]

        tolerance = 1e-15
        signalBySecurity = row.apply(lambda y:
                                     -1.0 if y < shortSecuritiesBound + tolerance else
                                     1.0 if y > longSecuritiesBound - tolerance else
                                     0.0)

        return signalBySecurity
