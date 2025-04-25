# Libraries
import requests
import pandas as pd
import re
# Other
from typing import List, Dict
from datetime import date,datetime,timedelta
from dateutil.relativedelta import *
# Fake User Agent
from fake_useragent import UserAgent
# Yahoo! Finance API
import yfinance as yf
import yahoo_fin.stock_info as yf_si

# Class PriceHistory is the class in charge of downloading the data. NASDAQ Version.
class PriceHistoryNASDAQ():
    """
    This is a simple Class object for scrapping price data from the NASDAQ website.
    """

    def __init__(self,symbols: List[str], user_agent: UserAgent) -> None:
        """
        Initializes the PriceHistory client

        Args:
        - symbols (List[str]): A list of ticker symbols to pull quotes for.
        """
        
        self._api_url = 'https://api.nasdaq.com/api/quote'
        self._api_service = 'historical'
        self._symbols = symbols
        self.user_agent = user_agent
        self.price_data_frame = self._build_data_frame()

    def _build_url(self, symbol: str) -> str:
        """
        Builds a full URL.

        Args:
        - symbol (str): The symbol you want to build a URL for.

        Returns:
        - A URL to the Ticker symbol provided.
        """

        parts = [self._api_url,symbol,self._api_service]
        return '/'.join(parts)
    
    @property
    def symbols(self) -> List[str]:
        """
        Returns all the symbols currently being pulled.

        Returns:
        - List[str]: A list of ticker symbols.
        """
        return self._symbols
    
    def _build_data_frame(self) -> pd.DataFrame:
        """
        Builds a data frame with all the price data.

        Returns:
        - pd.Dataframe: A Pandas Dataframe with the data cleaned and sorted.
        """

        all_data = []
        to_date = datetime.now().date()

        # Calculate start and end point
        from_date = to_date - relativedelta(months=6)

        for symbol in self._symbols:
            all_data = self._grab_prices(
                symbol=symbol,
                from_date=from_date,
                to_date=to_date,
            ) + all_data
        
        price_data_frame = pd.DataFrame(data=all_data)
        price_data_frame['date'] = pd.to_datetime(price_data_frame['date'])

        return price_data_frame
    
    def _grab_prices(self,symbol: str, from_date: date, to_date: date) -> List[Dict]:
        """
        Grabs the prices.

        Args:
        - symbol (str): The symbol to pull prices for.
        - from_date (date): The starting date to pull prices.
        - to_date (date): The ending data to pull prices for.

        Returns:
        - List[Dict]: A list of candle dictionaries.
        """

        # Build the URL
        price_url = self._build_url(symbol=symbol)
        
        # Calculate the limit
        limit: timedelta = (to_date - from_date)

        # Define the parameters
        params = {
            'fromdate': from_date.isoformat(),
            'todate': to_date.isoformat(),
            'assetclass': 'stocks',
            'limit': limit.days # Daily frequency data.
        }

        # Fake the headers
        headers = {'user-agent': self.user_agent}

        # Grab the historical data
        historical_data = requests.get(
            url=price_url,
            params=params,
            headers=headers,
            verify=True
        )

        # If it's ok, parse it
        if historical_data.ok:
            historical_data = historical_data.json()
            historical_data = historical_data['data']['tradesTable']['rows'] 
        
            # Clean the data
            for table_row in historical_data:
                table_row['symbol'] = symbol
                table_row['close'] = float(re.sub('[$,]', '', table_row['close']))
                table_row['volume'] = int(table_row['volume'].replace(',',''))
                table_row['open'] = float(re.sub('[$,]', '', table_row['open']))
                table_row['high'] = float(re.sub('[$,]', '', table_row['high']))
                table_row['low'] = float(re.sub('[$,]', '', table_row['low']))

            return historical_data

# DolarPrices is the class in charge of downloading CCL dolar data, using DolarApi.com
class DolarPrices():
    """
    This is a simple Class object for scrapping dolar price data in ARS from ArgentinaDatos API
    """
    
    def __init__(self) -> None:
        self._api_url =  'https://api.argentinadatos.com/v1/'
        self._api_service = 'cotizaciones/dolares' 
        
    def _build_url(self, symbol: str) -> str:
        """
        Builds a full URL.

        Args:
        - symbol (str): The symbol you want to build a URL for.
        You can choose between oficial, blue, bolsa, cripto, mayorista, solidario, and turista

        Returns:
        - A URL to the dollar symbol provided.
        """
        parts = [self._api_url,self._api_service,symbol]
        return '/'.join(parts)
    
    def _build_data_frame(self,symbol: str) -> pd.DataFrame:
        """
        Builds a data frame with all the price data.
        
        Args:
        - symbol (str): The symbol you want to build a URL for.
        You can choose between oficial, blue, bolsa, cripto, mayorista, solidario, and turista
        
        Returns:
        - pd.Dataframe: A Pandas Dataframe with the data cleaned and sorted.
        """
        full_url = self._build_url(symbol)
        
        dolar_data = requests.get(full_url).json()
        dolar_df = pd.DataFrame(dolar_data)
        dolar_df['fecha'] = pd.to_datetime(dolar_df['fecha'])
        dolar_df = dolar_df.set_index('fecha')[['venta']] # Filter sell price of dollars
        return dolar_df
        
           
# Class PriceHistory is the class in charge of downloading the data, Yahoo! Finance version.
class PriceHistoryYF():
    """
    This is a simple Class object for scrapping price data from the Yahoo! Finance website.
    """

    def __init__(self,symbols: List[str]) -> None:
        """
        Initializes the PriceHistory client

        Args:
        - symbols (List[str]): A list of ticker symbols to pull quotes for.
        """
        self._symbols = symbols
        self.price_data_frame = self._build_data_frame()
        
    def _build_url():
        pass
    
    @property
    def symbols(self) -> List[str]:
        """
        Returns all the symbols currently being pulled.

        Returns:
        - List[str]: A list of ticker symbols.
        """
        return self._symbols
    
    def _build_data_frame(self,from_date=None,to_date=None) -> pd.DataFrame:
        """
        Builds a data frame with all the price data.

        Args:
            Optional:
            - from_date: Starting date (default: six months from to_date)
            - to_date: Ending date (default: today)
        Returns:
        - pd.Dataframe: A Pandas Dataframe with the data cleaned and sorted.
        """
        # Calculate start and end point
        if to_date==None:
            to_date = datetime.now().date()
        if from_date==None:
            from_date = to_date - relativedelta(months=6)
        # Update data_frame and return
        self.price_data_frame = yf.download(self._symbols,start=from_date,end=to_date)
        return self.price_data_frame