import pandas as pd
import numpy as np
import unittest
import pandas.testing as pd_testing

"""
Write a function in Python to equalise the length of columns. Scenario: you have downloaded end of day pricing of multiple 
products via an API. You have found that some products have duplicate data on each column and some have missing values 
(NaN). Your task is to cleanse the data by equalising these data column enabling them to be compared with each other. i.e.
 remove duplicates and NaN values. Length of columns must match up to be equal once the function is run.
"""


def equalise_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    This function equalises the length of the columns for a given dataframe by removing duplicate
    and NA data. If a column value is a duplicate of the value from the previous row, the whole row
    is removed. If a row has an NA value in any column, the whole row is removed.

    Assumes that each row corresponds to data for a single date/datetime, denoted by a column with
    mnemonic 'DateTime'. Also assumes that the dataframe is already sorted by date. 

    Suppose we have two successive rows with some common column values.
    - If both rows have NAs, then both will be removed.
    - If only one of the rows has an NA, then that row will be removed.
    - If neither row has an NA, the we remove the second row.

    We do not want to remove rows that are non-consecutive. Prices move up and down, so we may have the
    same price today as we did a year ago, which is valid.

    Args:
        df (pd.DataFrame): the dataframe whose columns we wish to equalise.

    Returns:
        pd.DataFrame: the dataframe with equalised columns
    """

    # Identify the rows with duplicates
    # ---------------------------------

    # Get the column names we want to shift. All but the DateTime key column.
    colnames = df.columns.tolist()
    colnames.remove('DateTime')

    # Shift the columns one row forward and one back.
    kwargs_prev = {
        colname + '_prev': df[colname].shift(1) for colname in colnames}
    kwargs_next = {
        colname + '_next': df[colname].shift(-1) for colname in colnames}
    df = df.assign(**kwargs_prev, **kwargs_next)

    # Check whether there is a duplicate in the forward or backward rows across the individual columns
    kwargs_prev = {colname + '_prev_dup': df[colname]
                   == df[colname + '_prev'] for colname in colnames}
    kwargs_next = {colname + '_next_dup': df[colname]
                   == df[colname + '_next'] for colname in colnames}
    df = df.assign(**kwargs_prev, **kwargs_next)

    # Check whether there is a duplicate in the forward or backward rows across any column.
    kwargs_prev = {'has_prev_dup': df[kwargs_prev.keys()].any(axis='columns')}
    kwargs_next = {'has_next_dup': df[kwargs_next.keys()].any(axis='columns')}
    df = df.assign(**kwargs_prev, **kwargs_next)

    # Check whether there is a duplicate in both the forward and backward rows across any column.
    # These rows will usually be removed, conditional upon NAs in surrounding rows.
    df = df.assign(
        has_double_dup=df[['has_prev_dup', 'has_next_dup']].all(axis='columns'))
    df = df.assign(
        prev_has_double_dup=df['has_double_dup'].shift(1),
        next_has_double_dup=df['has_double_dup'].shift(-1),
    )

    # Identify rows with NAs
    # ----------------------

    df = df.assign(has_na=df[colnames].isnull().values.any(axis=1))
    df = df.assign(prev_has_na=df['has_na'].shift(1))
    # needed for a corner case.
    df = df.assign(prev_2_has_na=df['has_na'].shift(2))

    # Identify the rows to remove
    # ---------------------------

    def removal_conditions(dst: pd.DataFrame) -> pd.DataFrame:
        """The set of rules for the removing conditions"""
        # Rows with an NA are removed always.
        if dst['has_na']:
            return True
        # Rows with a duplicate with the previous and the next row ('double' duplicate) are removed.
        elif (dst['has_double_dup']):
            # If the previous row has an NA, then do not remove.
            if (dst['prev_has_na'] == True):
                return False
            else:
                return True
        # If the prev row has "double" duplicate, then the current row is not removed, conditional on NA.
        elif (dst['prev_has_double_dup'] == True):
            # Corner Case: If the row prior to the previous is an NA, then the current row is removed.
            if (dst['prev_2_has_na'] == True):
                return True
            else:
                return False
        # If the next row has a "double" duplicate, then the current row is not removed.
        elif (dst['next_has_double_dup'] == True):
            return False
        # We remove the current row if it is a duplicate of the previous, unless the previous was an NA.
        elif (dst['has_prev_dup']):
            if (dst['prev_has_na'] == True):
                return False
            else:
                return True
        else:
            return False

    df['remove'] = df.apply(removal_conditions, axis=1)

    # Remove the rows with duplicates or NAs
    # --------------------------------------

    df = df[df['remove'] == False]
    colnames.insert(0, 'DateTime')
    df = df[colnames].reset_index(drop=True)
    return df


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
