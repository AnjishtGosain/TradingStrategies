import pandas as pd
import numpy as np
import unittest
import pandas.testing as pd_testing

from YahooDataScraper.equalise_columns import equalise_columns


class TestEqualiseColumns(unittest.TestCase):
    def assertDataframeEqual(self, a, b, msg):
        try:
            pd_testing.assert_frame_equal(a, b)
        except AssertionError as e:
            raise self.failureException(msg) from e

    def setUp(self):
        self.addTypeEqualityFunc(pd.DataFrame, self.assertDataframeEqual)

    def test_1_1(self):
        """Tests whether a row that is duplicate with the previous row is correctly removed.
        """
        in_df = pd.DataFrame([
            ['20200101', 1, 2, 2],
            ['20200102', 3, 3, 4],
            ['20200103', 1, 3, 2],
            ['20200105', 13, 2, 1]
        ],
            columns=['DateTime', 'a', 'b', 'c'])
        in_df['DateTime'] = pd.to_datetime(in_df['DateTime'])

        out_df = pd.DataFrame([
            ['20200101', 1, 2, 2],
            ['20200102', 3, 3, 4],
            ['20200105', 13, 2, 1]
        ],
            columns=['DateTime', 'a', 'b', 'c'])
        out_df['DateTime'] = pd.to_datetime(out_df['DateTime'])

        test_df = equalise_columns(in_df)
        self.assertEqual(out_df, test_df)

    def test_1_2(self):
        """Tests whether a row that is duplicate with the previous row is correctly removed.
        """
        in_df = pd.DataFrame([
            ['20200101', 1, 2, 2],
            ['20200102', 3, 3, 4],
            ['20200103', 1, 3, 2],
            ['20200104', 5, 1, 10],
            ['20200105', 7, 1, 2]
        ],
            columns=['DateTime', 'a', 'b', 'c'])
        in_df['DateTime'] = pd.to_datetime(in_df['DateTime'])

        out_df = pd.DataFrame([
            ['20200101', 1, 2, 2],
            ['20200102', 3, 3, 4],
            ['20200104', 5, 1, 10]
        ],
            columns=['DateTime', 'a', 'b', 'c'])
        out_df['DateTime'] = pd.to_datetime(out_df['DateTime'])

        test_df = equalise_columns(in_df)
        self.assertEqual(out_df, test_df)

    def test_2_1(self):
        """Tests whether a row that is duplicate with the previous and next row is correctly removed.
        """
        in_df = pd.DataFrame([
            ['20200101', 1, 2, 2],
            ['20200102', 3, 3, 4],
            ['20200103', 1, 3, 2],
            ['20200104', 5, 1, 2],
            ['20200105', 13, 2, 1]
        ],
            columns=['DateTime', 'a', 'b', 'c'])
        in_df['DateTime'] = pd.to_datetime(in_df['DateTime'])

        out_df = pd.DataFrame([
            ['20200101', 1, 2, 2],
            ['20200102', 3, 3, 4],
            ['20200104', 5, 1, 2],
            ['20200105', 13, 2, 1]
        ],
            columns=['DateTime', 'a', 'b', 'c'])
        out_df['DateTime'] = pd.to_datetime(out_df['DateTime'])

        test_df = equalise_columns(in_df)
        self.assertEqual(out_df, test_df)

    def test_2_2(self):
        """Tests whether multiple rows that are duplicate with the previous and next are correctly removed.
        """
        in_df = pd.DataFrame([
            ['20200101', 1, 2, 2],
            ['20200102', 3, 3, 4],
            ['20200103', 1, 3, 2],
            ['20200104', 5, 1, 2],
            ['20200105', 7, 1, 2],
            ['20200106', 13, 1, 1]
        ],
            columns=['DateTime', 'a', 'b', 'c'])
        in_df['DateTime'] = pd.to_datetime(in_df['DateTime'])

        out_df = pd.DataFrame([
            ['20200101', 1, 2, 2],
            ['20200102', 3, 3, 4],
            ['20200106', 13, 1, 1]
        ],
            columns=['DateTime', 'a', 'b', 'c'])
        out_df['DateTime'] = pd.to_datetime(out_df['DateTime'])

        test_df = equalise_columns(in_df)
        self.assertEqual(out_df, test_df)

    def test_3(self):
        """Tests whether rows with NAs are removed correctly. No duplicates.
        """
        in_df = pd.DataFrame([
            ['20200101', 1.0, np.NaN, 2.0],
            ['20200102', 3.0, 3.0, 4.0],
            ['20200103', 1.0, 4.0, 2.0],
            ['20200105', 13.0, 2.0, np.NaN]
        ],
            columns=['DateTime', 'a', 'b', 'c'])
        in_df['DateTime'] = pd.to_datetime(in_df['DateTime'])

        out_df = pd.DataFrame([
            ['20200102', 3.0, 3.0, 4.0],
            ['20200103', 1.0, 4.0, 2.0]
        ],
            columns=['DateTime', 'a', 'b', 'c'])
        out_df['DateTime'] = pd.to_datetime(out_df['DateTime'])

        test_df = equalise_columns(in_df)
        self.assertEqual(out_df, test_df)

    def test_4_1(self):
        """Tests whether rows with NAs and duplicates are removed correctly.
        """
        in_df = pd.DataFrame([
            ['20200101', 1.0, np.NaN, 2.0],
            ['20200102', 3.0, 3.0, 4.0],
            ['20200103', 1.0, 4.0, 2.0],
            ['20200104', 2.0, 2.0, 3.0],
            ['20200105', 13.0, 2.0, np.NaN]
        ],
            columns=['DateTime', 'a', 'b', 'c'])
        in_df['DateTime'] = pd.to_datetime(in_df['DateTime'])

        out_df = pd.DataFrame([
            ['20200102', 3.0, 3.0, 4.0],
            ['20200103', 1.0, 4.0, 2.0],
            ['20200104', 2.0, 2.0, 3.0]
        ],
            columns=['DateTime', 'a', 'b', 'c'])
        out_df['DateTime'] = pd.to_datetime(out_df['DateTime'])

        test_df = equalise_columns(in_df)
        self.assertEqual(out_df, test_df)

    def test_4_2(self):
        """Tests whether rows with NAs and duplicates are removed correctly. 
        """
        in_df = pd.DataFrame([
            ['20200101', 1.0, np.NaN, 2.0],
            ['20200102', 3.0, 3.0, 4.0],
            ['20200103', 1.0, 4.0, 2.0],
            ['20200104', 2.0, 2.0, np.NaN],
            ['20200105', 13.0, 2.0, 1.0]
        ],
            columns=['DateTime', 'a', 'b', 'c'])
        in_df['DateTime'] = pd.to_datetime(in_df['DateTime'])

        out_df = pd.DataFrame([
            ['20200102', 3.0, 3.0, 4.0],
            ['20200103', 1.0, 4.0, 2.0],
            ['20200105', 13.0, 2.0, 1.0]
        ],
            columns=['DateTime', 'a', 'b', 'c'])
        out_df['DateTime'] = pd.to_datetime(out_df['DateTime'])

        test_df = equalise_columns(in_df)
        self.assertEqual(out_df, test_df)

    def test_5_1(self):
        """Tests whether a row that is duplicate with the previous and next row, but both these have an NA.
        """
        in_df = pd.DataFrame([
            ['20200101', 1.0, 2.0, 2.0],
            ['20200102', 3.0, 3.0, np.NaN],
            ['20200103', 1.0, 3.0, 2.0],
            ['20200104', 5.0, np.NaN, 2.0],
            ['20200105', 13.0, 2.0, 1.0]
        ],
            columns=['DateTime', 'a', 'b', 'c'])
        in_df['DateTime'] = pd.to_datetime(in_df['DateTime'])

        out_df = pd.DataFrame([
            ['20200101', 1.0, 2.0, 2.0],
            ['20200103', 1.0, 3.0, 2.0],
            ['20200105', 13.0, 2.0, 1.0]
        ],
            columns=['DateTime', 'a', 'b', 'c'])
        out_df['DateTime'] = pd.to_datetime(out_df['DateTime'])

        test_df = equalise_columns(in_df)
        self.assertEqual(out_df, test_df)

    def test_5_2(self):
        """Tests whether a row that is duplicate with the previous and next row, but previous has an NA.
        """
        in_df = pd.DataFrame([
            ['20200101', 1.0, 2.0, 2.0],
            ['20200102', 3.0, 3.0, np.NaN],
            ['20200103', 1.0, 3.0, 2.0],
            ['20200104', 5.0, 1.0, 2.0],
            ['20200105', 13.0, 2.0, 1.0]
        ],
            columns=['DateTime', 'a', 'b', 'c'])
        in_df['DateTime'] = pd.to_datetime(in_df['DateTime'])

        out_df = pd.DataFrame([
            ['20200101', 1.0, 2.0, 2.0],
            ['20200103', 1.0, 3.0, 2.0],
            ['20200105', 13.0, 2.0, 1.0]
        ],
            columns=['DateTime', 'a', 'b', 'c'])
        out_df['DateTime'] = pd.to_datetime(out_df['DateTime'])

        test_df = equalise_columns(in_df)
        self.assertEqual(out_df, test_df)

    def test_5_3(self):
        """Tests whether a row that is duplicate with the previous and next row, but next has an NA.
        """
        in_df = pd.DataFrame([
            ['20200101', 1.0, 2.0, 2.0],
            ['20200102', 3.0, 3.0, 1.0],
            ['20200103', 1.0, 3.0, 2.0],
            ['20200104', np.NaN, 1.0, 2.0],
            ['20200105', 13.0, 2.0, 1.0]
        ],
            columns=['DateTime', 'a', 'b', 'c'])
        in_df['DateTime'] = pd.to_datetime(in_df['DateTime'])

        out_df = pd.DataFrame([
            ['20200101', 1.0, 2.0, 2.0],
            ['20200102', 3.0, 3.0, 1.0],
            ['20200105', 13.0, 2.0, 1.0]
        ],
            columns=['DateTime', 'a', 'b', 'c'])
        out_df['DateTime'] = pd.to_datetime(out_df['DateTime'])

        test_df = equalise_columns(in_df)
        self.assertEqual(out_df, test_df)


if __name__ == '__main__':
    unittest.main()
