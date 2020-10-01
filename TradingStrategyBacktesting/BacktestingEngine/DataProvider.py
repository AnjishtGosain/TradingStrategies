import pandas
import math

from pathlib import Path

from Common.Enumerations.CacheType import CacheType
from Common.Enumerations.FactorName import FactorName 
from Common.Enumerations.ReturnType import ReturnType 

class DataProvider(object):

    @staticmethod
    def FilteredCachedLoad(inputCachePath: Path, filename : str, cacheType = CacheType.Csv) -> pandas.DataFrame():
        '''
        Loads in the returns and factor data, and cleans it as required by the specified factor.
        '''

        # Load in the data as a pandas data frame.
        # ----------------------------------------

        pivotedDataDict = DataProvider.CachedLoad(inputCachePath, filename, cacheType) 

        # Mix the forward and backwards returns
        # -------------------------------------

        # The data set contains forward and backwards returns. Upon manual checking, it is confirmed that the forward return on day n for security i is equal to
        # the backward return on day n + 1 for security i. As there are instances where the forward return is missing, a new returns series is constructed based on
        # the mixture of the two. 

        forwardReturnsDF = pivotedDataDict[ReturnType.Forward]
        backwardReturnsDF = pivotedDataDict[ReturnType.Backward]
        mixedReturnsDF = forwardReturnsDF.copy(deep = True)

        for i in range(len(mixedReturnsDF.index) - 1):
            currentIndexValue = mixedReturnsDF.index[i]
            nextIndexValue = mixedReturnsDF.index[i + 1] 
            # If row is all zeros, then select the backward returns
            row = mixedReturnsDF.loc[currentIndexValue] 
            if row.min() == 0.0 and row.max() == 0.0:
                for j in mixedReturnsDF.columns:
                    mixedReturnsDF.at[currentIndexValue, j] = backwardReturnsDF.at[nextIndexValue, j] 
            # Override the null values with the back returns
            else:
                for j in mixedReturnsDF.columns:
                    if math.isnan(mixedReturnsDF.at[currentIndexValue, j]):
                        mixedReturnsDF.at[currentIndexValue, j] = backwardReturnsDF.at[nextIndexValue, j]

        pivotedDataDict[ReturnType.Mixed] = mixedReturnsDF

        return pivotedDataDict


    @staticmethod
    def CachedLoad(inputCachePath: Path, filename : str, cacheType = CacheType.Csv) -> pandas.DataFrame():
        '''
        Loads in the returns and factor data as a pandas data frame.
        '''

        if(cacheType == CacheType.Csv):
            # Read in the data from cache location
            rawDataFilePath = inputCachePath / filename 
            rawDataDF = pandas.read_csv(rawDataFilePath)

            # Rename the columns to assist with editor tab completion and code maintainability
            DataProvider.__RenameCsvColumns(rawDataDF)

            # Change the data type for date and security id 
            rawDataDF["DateTime"] = pandas.to_datetime(rawDataDF["DateTime"], format = "%Y-%m-%d") # parse string date to DateTime
            rawDataDF["SecurityId"] = rawDataDF["SecurityId"].astype(int) # the security ids are strictly integers

            # Pivot the dataset into a pandas friendly format
            pivotedDataDict = {}
            for column in rawDataDF.columns:
                if column != "DataTime" and column != "SecurityId":
                    pivotedDataDict[column] = rawDataDF.pivot(index = "DateTime", columns = "SecurityId", values = column)

            return pivotedDataDict

        else:
            raise NotImplementedError("Cached load is currently only supported for Csv.")

    @staticmethod
    def __RenameCsvColumns(csvDataDF : pandas.DataFrame):
        # This function loops through the columns names of the cached data and renames them using a parser. 
        newColumnNames = {x : DataProvider.__ParseColumnName(x) for x in csvDataDF.columns.values}
        csvDataDF.rename(columns = newColumnNames, inplace = True)

    @staticmethod
    def __ParseColumnName(columnNameStr : str):
        # Parser for renaming dataframe column names
        lowerColumnNameStr = columnNameStr.lower()
        if lowerColumnNameStr == "date":
            return "DateTime"
        elif lowerColumnNameStr == "id_security":
            return "SecurityId"
        elif lowerColumnNameStr == "fm_1wd" or lowerColumnNameStr == "forwardreturn":
            return ReturnType.Forward
        elif lowerColumnNameStr == "m_1wd" or lowerColumnNameStr == "backwardreturn":
            return ReturnType.Backward
        elif lowerColumnNameStr == "factor_1" or lowerColumnNameStr == "factor1":
            return FactorName.Factor1 
        elif lowerColumnNameStr == "factor_2" or lowerColumnNameStr == "factor2":
            return FactorName.Factor2 
        else:
            raise NotImplementedError("Unrecognised column name.")
            


       

        


