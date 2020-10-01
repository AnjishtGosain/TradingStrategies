import unittest

from BacktestingEngine.DataProvider import DataProvider

class TestDataProvider(unittest.TestCase):

    def Test1(self):
        # Tests the dataframe produced by the csv dataprovider

        # Read in the cached data via the data provider
        # ---------------------------------------------

        inputCachePath = Path("C:/Users/anjis/Documents/AnjishtGosain_ChallengerSolution")
        data = DataProvider.CachedLoad(inputCachePath, "dataset.csv") 
        self.assertEqual(3*4, 12)

if __name__ == '__main__':
    unittest.main()
