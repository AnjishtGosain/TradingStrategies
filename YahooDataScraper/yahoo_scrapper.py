from selenium import webdriver
from bs4 import BeautifulSoup
from enum import Enum, auto
import pandas as pd
import time
import datetime
import ntpath
import os
import re

"""
Create a DataFrame in Python using the following instructions: 1) Visit yahoo finance 2) choose 3 of your 
favourite stocks, 3 interest rate products and 3 Crypto-currencies. 3) Download CSV files of closing or 
adjusted closing price of a chosen time frame. (5min, 15min, daily, weekly etc) 4) Create a DataFrame in 
Python with column headers as closing prices of each product and rows for the chosen time frame. 5) there 
is no need to go back a long time in history just a few weeks to a month is enough as the exercise tests 
your ability to create DataFrames in python. 6) please copy and paste your entire code block below for 
use to read through to understand your coding abilities.
"""


class DataFrequency(Enum):
    """
    Enumeration for the different data frequencies that can be downloaded from Yahoo. 
    """
    Daily = auto()
    Weekly = auto()
    Monthly = auto()


class DataFrequencyExtensions:

    @staticmethod
    def to_string(data_frequency: DataFrequency, variant=0) -> str:
        """
        Converts a given DataFrequency to a string. e.g. used in getting the Yahoo URL.

        Args:
            data_frequency (DataType): The name of the data frequency we wish to map to a string.
            variant (int): The variant of the string to return.

        Returns:
            str: The string for the data frequency.
        """
        mapping = {
            DataFrequency.Daily: ('Daily', '1d'),
            DataFrequency.Weekly: ('Weekly', '1wk'),
            DataFrequency.Monthly: ('Monthly', '1mo')
        }
        return mapping[data_frequency][variant]


class DataType(Enum):
    """
    Enumeration for the different data types that can be downloaded from Yahoo.
    """
    Open = auto()
    High = auto()
    Low = auto()
    Close = auto()
    AdjustedClose = auto()
    TradedVolume = auto()


class DataTypeExtensions:

    @staticmethod
    def to_string(data_type: DataType, variant=0) -> str:
        """
        Converts a given DataType to a string. Used to convert column names from string to enum.

        Args:
            data_type (DataType): The name of the data type we wish to map to a string.
            variant (int): The variant of the string to return.

        Returns:
            str: The string for the data type.
        """
        mapping = {
            DataType.Open: ('Open', 'Open'),
            DataType.High: ('High', 'High'),
            DataType.Low: ('Low', 'Low'),
            DataType.Close: ('Close', 'Close'),
            DataType.AdjustedClose: ('Adj Close', 'AdjustedClose'),
            DataType.TradedVolume: ('Volume', 'TradedVolume'),

        }
        return mapping[data_type][variant]


class YahooTicker(Enum):
    """
    Enumeration for the supported security tickers.
    """
    BHP = auto()  # BHP Billiton ASX
    CBA = auto()  # Commonwealth Bank of Australia ASX
    RIO = auto()  # Rio Tinto ASX
    BTC = auto()  # Bitcoin USD
    ETH = auto()  # Ethereum USD
    LTC = auto()  # Litecoin USD
    FVX = auto()  # US Treasury Yield 5 Years
    TNX = auto()  # US Treasury Yield 10 Years
    TYX = auto()  # US Treasury Yield 30 Years


class YahooTickerExtensions:

    @staticmethod
    def to_string(ticker: YahooTicker, variant=0) -> str:
        """
        Converts a human understandable ticker enumeration to a string. 

        Args:
            ticker (YahooTicker): The name of the Yahoo Ticker we wish to map to a string.
            variant (int): The variant of the ticker string to return.

        Returns:
            str: The string for the Yahoo Ticker.
        """
        ticker_mapping = {
            YahooTicker.BHP: ('BHP', 'BHP.AX', 'BHP.AX'),
            YahooTicker.CBA: ('CBA', 'CBA.AX', 'CBA.AX'),
            YahooTicker.RIO: ('RIO', 'RIO', 'RIO'),
            YahooTicker.BTC: ('BTC', 'BTC-USD', 'BTC-USD'),
            YahooTicker.ETH: ('ETH', 'ETH-USD', 'ETH-USD'),
            YahooTicker.LTC: ('LTC', 'LTC-USD', 'LTC-USD'),
            YahooTicker.FVX: ('FVX', r'^FVX', r'%5EFVX'),
            YahooTicker.TNX: ('TNX', r'^TNX', r'%5ETNX'),
            YahooTicker.TYX: ('TYX', r'^TYX', r'%5ETYX')
        }
        return ticker_mapping[ticker][variant]

    @staticmethod
    def is_interest_rate_product(ticker: YahooTicker) -> bool:
        """Determines whether the specified ticker is an interest rate product.

        Args:
            ticker (YahooTicker): The enumeration of the ticker. 

        Returns:
            bool: Returns True if the ticker is an interest rate product. 
        """
        if ticker == YahooTicker.FVX:
            return True
        elif ticker == YahooTicker.TNX:
            return True
        elif ticker == YahooTicker.TYX:
            return True
        else:
            return False


class YahooDataConnection:

    def __init__(self, yahoo_url=None, download_path=None, is_chrome_headless=None,
                 selenium_sleep_time=None):
        """
        Default constructor for the Yahoo data connection.

        Args:
            yahoo_url ([type], optional): String value with the yahoo finance url. 
            download_path ([type], optional): String for the os path where the data is downloaded.
            is_chrome_headless ([type], optional): Boolean for whether to open Chrome GUI. 
            selenium_sleep_time ([type], optional): Int specifying the number of seconds given for 
                pages to load.

        """
        if yahoo_url is None:
            yahoo_url = 'https://au.finance.yahoo.com/'
        if download_path is None:
            download_path = 'C:/tmp'
        if is_chrome_headless is None:
            is_chrome_headless = True
        if selenium_sleep_time is None:
            selenium_sleep_time = 10
        self.yahoo_url = yahoo_url
        self.download_path = download_path
        self.is_chrome_headless = is_chrome_headless
        self.selenium_sleep_time = selenium_sleep_time

        # Instantiate the Chrome browser
        self.__initialise_chrome_browser()

    def __initialise_chrome_browser(self):
        """"
        Creates a new Chrome session for the Selenium driver to use. 
        """
        options = webdriver.ChromeOptions()
        if self.is_chrome_headless:
            options.add_argument('headless')
        if self.download_path is not None:
            # Create the download path if it does not exist
            if not os.path.exists(self.download_path):
                os.makedirs(self.download_path)
            # If the OS is windows, then we need to convert to a Windows path.
            download_path = self.download_path
            if os.name == 'nt':
                download_path = self.download_path.replace('/', ntpath.sep)
            # Specify the download path for the Chrome browser
            prefs = {}
            prefs['profile.default_content_settings.popups'] = 0
            prefs['download.default_directory'] = download_path
            options.add_experimental_option('prefs', prefs)

        self.__browser = webdriver.Chrome(chrome_options=options)

    def __get_url(self, ticker: YahooTicker, data_frequency: DataFrequency, start_date: str,
                  end_date: str) -> str:
        """
        Converts a human understandable ticker, data frequency, and start and end dates, to the Yahoo url. 

        Args:
            ticker (YahooTicker): The name of the Yahoo Ticker we wish to map to a website ticker.
            data_frequency (DataFrequency): The frequency of the data to retrieve.
            start_date (str): The start date for the data, in yyyymmdd format.
            end_date (str): The end date for the data, in yyyymmdd format.

        Returns:
            str: The Yahoo url for the ticker.
        """
        ticker_str = YahooTickerExtensions.to_string(ticker, 2)
        freq_str = DataFrequencyExtensions.to_string(data_frequency, 1)
        start_date_unix = time.mktime(
            datetime.datetime.strptime(start_date, r'%Y%m%d').timetuple())
        end_date_unix = time.mktime(
            datetime.datetime.strptime(end_date, r'%Y%m%d').timetuple())
        ticker_url = (self.yahoo_url + '/quote/' + ticker_str + '/history?'
                      'period1=' + str(int(start_date_unix)) + '&' +
                      'period2=' + str(int(end_date_unix)) + '&' +
                      'interval=' + freq_str + '&filter=history&frequency=' + freq_str)
        return ticker_url

    def __get_download_filename(self, ticker: YahooTicker) -> str:
        """
        Returns the name of the data file that is downloaded from Yahoo for a given ticker. 

        Args:
            ticker (YahooTicker): The name of the Yahoo Ticker we wish to map to a website ticker.

        Returns:
            str: The path of the file that is downloaded for the ticker.
        """
        ticker_string = YahooTickerExtensions.to_string(ticker, 1)
        filename = os.path.join(self.download_path, ticker_string + '.csv')
        return filename

    def __get_cache_filename(self, ticker: YahooTicker, data_frequency: DataFrequency, start_date: str,
                             end_date: str) -> str:
        """
        Converts a human understandable ticker, data frequency, and start and end dates, into a
        filename for the cache. 

        Args:
            ticker (YahooTicker): The name of the Yahoo Ticker we wish to map to a website ticker.
            data_frequency (DataFrequency): The frequency of the data to retrieve.
            start_date (str): The start date for the data, in yyyymmdd format.
            end_date (str): The end date for the data, in yyyymmdd format.

        Returns:
            str: The filename in the cache. 
        """
        ticker_str = YahooTickerExtensions.to_string(ticker, 1)
        freq_str = DataFrequencyExtensions.to_string(data_frequency, 1)
        filename_str = '_'.join([ticker_str, freq_str, start_date, end_date])
        filename_path = os.path.join(self.download_path, filename_str + '.csv')
        return filename_path

    def __download_data(self, ticker: YahooTicker, data_frequency: DataFrequency, start_date: str,
                        end_date: str):
        """
        Downloads the specified ticker's historical price data from the Yahoo website.  

        # Note that this function requies the user to install ChromeDriver. 

        Args:
            ticker (YahooTicker): The name of the financial security of interest.
            data_frequency (DataFrequency): The frequency of the data to retrieve.
            start_date (str): The start date for the data, in %yyyy%mm%dd format.
            end_date (str): The end date for the data, in %yyyy%mm%dd format.
        """

        # Check if data exists in the cache
        download_filename = self.__get_download_filename(ticker=ticker)
        cache_filename = self.__get_cache_filename(ticker=ticker, data_frequency=data_frequency,
                                                   start_date=start_date, end_date=end_date)
        if not os.path.isfile(cache_filename):
            # Construct the URL specific for the ticker
            ticker_url = self.__get_url(
                ticker=ticker, data_frequency=data_frequency, start_date=start_date,
                end_date=end_date)

            # Load the URL for the ticker in the browser
            self.__browser.get(ticker_url)

            # Sleep a specified period of time to allow the page to load.
            time.sleep(self.selenium_sleep_time)

            # Click the 'Download' button
            download_css = r'#Col1-1-HistoricalDataTable-Proxy > section > div.Pt\(15px\) > div.C\(\$tertiaryColor\).Mt\(20px\).Mb\(15px\) > span.Fl\(end\).Pos\(r\).T\(-6px\) > a > span'
            download_button = self.__browser.find_element_by_css_selector(
                download_css)
            download_button.click()

            # Wait for the file to finish downloading before proceeding to the next step
            file_not_downloaded = True
            while file_not_downloaded:
                # If file does not exist, wait some time
                if os.path.isfile(download_filename):
                    file_not_downloaded = False
                    os.rename(download_filename, cache_filename)
                else:
                    time.sleep(self.selenium_sleep_time)

    def get_historical_data(self, tickers: [YahooTicker], data_types: [DataType],
                            data_frequency: DataFrequency, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Gets the data from for the desired tickers.  

        Args:
            tickers ([YahooTicker]): The list of the tickers for which to retrieve data.
            data_types ([DataType]): The list of the data types to retrieve.
            data_frequency (DataFrequency): The frequency of the data to retrieve.
            start_date (str): The start date for the data, in %yyyy%mm%dd format.
            end_date (str): The end date for the data, in %yyyy%mm%dd format.

        Returns:
            pd.DataFrame: The merge dataframe of the requested price data.
        """

        df = pd.DataFrame(columns=['Date'])
        for ticker in tickers:
            # Download the data for the ticker
            self.__download_data(
                ticker=ticker, data_frequency=data_frequency, start_date=start_date, end_date=end_date)

            # Read in the csv data
            filename = self.__get_cache_filename(
                ticker=ticker, data_frequency=data_frequency, start_date=start_date, end_date=end_date)
            ticker_df = pd.read_csv(filename)

            # Prefix the desired price column with the ticker, and merge data
            rename_cols = {DataTypeExtensions.to_string(data_type, 0): YahooTickerExtensions.to_string(
                ticker) + '_' + DataTypeExtensions.to_string(data_type, 1) for data_type in data_types}
            ticker_df = ticker_df.rename(columns=rename_cols)
            ticker_df = ticker_df[['Date'] + list(rename_cols.values())]
            df = df.merge(ticker_df, on='Date', how='outer')

        # Sort the columns by date. Data may be available for different dates for each ticker.
        df = df.sort_values(by=['Date'])
        df = df.reset_index(drop=True)
        return df


if __name__ == '__main__':
    yahoo_conn = YahooDataConnection()

    df = yahoo_conn.get_historical_data(tickers=[
        YahooTicker.BHP,
        YahooTicker.CBA,
        YahooTicker.RIO,
        YahooTicker.BTC,
        YahooTicker.ETH,
        YahooTicker.LTC,
        YahooTicker.TNX,
        YahooTicker.TYX,
        YahooTicker.FVX
    ],
        data_types=[DataType.AdjustedClose, DataType.Close],
        data_frequency=DataFrequency.Weekly,
        start_date='20180929',
        end_date='20200929'
    )
