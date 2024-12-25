from polygon import RESTClient
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os
import time
import json
from pathlib import Path
import pandas_market_calendars as mcal

load_dotenv()

TICKER_TYPE =  [
  'FUND', # Investment Funds - Can focus on income-generating strategies
  'ETF',  # Exchange Traded Funds - Many ETFs specifically track high-dividend stocks
  'BOND', # Bonds - Provides fixed interest payments
  'CS'    # Common Stock - Can be filtered for high-dividend paying companies
] 

# Pre-load exchange calendars for major US exchanges
EXCHANGE_CALENDARS = {
    'XNYS': mcal.get_calendar('NYSE'),     # New York Stock Exchange
    'XNAS': mcal.get_calendar('NASDAQ'),   # NASDAQ
    'XASE': mcal.get_calendar('NYSE')      # NYSE American (uses NYSE calendar)
}

def sleep_if_not_subscribed():
    if not os.getenv("IS_POLYGON_SUBSCRIBED"):
        time.sleep(12)

def get_previous_trading_day(date_str, exchange_mic='XNYS'):
    """
    Get the previous trading day for a given date using pre-loaded calendars
    Args:
        date_str: Date string in format 'YYYY-MM-DD'
        exchange_mic: Market Identifier Code for the exchange
    Returns:
        Previous trading day in format 'YYYY-MM-DD'
    Raises:
        ValueError: If exchange_mic is invalid or no trading days found
    """
    # Validate exchange MIC
    if exchange_mic not in EXCHANGE_CALENDARS:
        raise ValueError(f"Invalid exchange MIC: {exchange_mic}. Valid MICs are: {list(EXCHANGE_CALENDARS.keys())}")
    
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
        
        # Get trading days using pre-loaded calendar
        trading_days = EXCHANGE_CALENDARS[exchange_mic].valid_days(
            start_date=date - timedelta(days=15),
            end_date=date
        ).tz_localize(None)  # Remove timezone info from trading days
        
        # Find the last trading day before the given date
        previous_trading_days = trading_days[trading_days < date]
        if len(previous_trading_days) == 0:
            raise ValueError(f"No trading days found in the 10 days before {date_str} for exchange {exchange_mic}")
            
        return previous_trading_days[-1].strftime("%Y-%m-%d")
        
    except ValueError as e:
        raise e
    except Exception as e:
        raise ValueError(f"Error getting previous trading day: {str(e)}")

def check_and_save_dividend_data(client, ticker):
    print(f"\nAnalyzing dividend yield for {ticker['ticker']}...")
    ticker_id = ticker['ticker']

    dividend_data = client.list_dividends(
        ticker=ticker_id,
        order="desc",
    )

    dividend_list = list(dividend_data)
    
    if not dividend_list:
        print(f"No dividend data found for {ticker['ticker']}")
        return None

    current_date = datetime.now().date()
    
    latest_dividend = None
    for div in dividend_list:
        ex_date = datetime.strptime(div.ex_dividend_date, "%Y-%m-%d").date()
        if ex_date < current_date:
            latest_dividend = div
            break
    
    if not latest_dividend:
        print(f"No historical dividend data found for {ticker['ticker']}")
        return None

    try:
        # Get the previous trading day before ex-dividend date
        ex_day = get_previous_trading_day(latest_dividend.ex_dividend_date)
        print(f"Using closing price from previous trading day: {ex_day}")
        
        sleep_if_not_subscribed()

        ex_day_data = client.get_daily_open_close_agg(
            ticker=ticker_id, 
            date=ex_day
        )

        # Calculate estimated yearly yield
        dividend_yield = (latest_dividend.cash_amount / ex_day_data.close) * 100

        if dividend_yield < 2:
            print(
                f"The last dividend yield is too low ({dividend_yield:.2f}%), skipping {ticker}"
            )
            return None

        print("Yield is high enough, saving dividend data...")
        
        # Save raw API response to JSON
        output_path = Path(f"dividend_data_{ticker_id}.json")
        with open(output_path, "w") as f:
            json.dump(dividend_list, f, indent=2, default=lambda x: x.__dict__)

        print(f"Dividend data saved to: {output_path.absolute()}")
        return dividend_list

    except Exception as e:
        print(f"Error processing dividend data: {str(e)}")
        return None


def main():
    client = RESTClient(api_key=os.getenv("POLYGON_API_KEY"))
    
    tickers_file = "us_major_tickers.json"
    with open(tickers_file, 'r') as f:
        tickers_data = json.load(f)
    
        for ticker in tickers_data:
            if ticker['type'] not in TICKER_TYPE:
                print(f"Skipping {ticker['ticker']} because it's not a valid stock in {TICKER_TYPE}")
                continue
            
            check_and_save_dividend_data(client, ticker)
            sleep_if_not_subscribed()
        
if __name__ == "__main__":
    main()
