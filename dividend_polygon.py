from polygon import RESTClient
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os
import time
import json
from pathlib import Path

load_dotenv()


def get_first_dividend(generator):
    """Safely get first item from generator without consuming all items"""
    try:
        return next(generator)
    except StopIteration:
        return None


def check_and_save_dividend_data(client, ticker):
    print(f"\nAnalyzing dividend yield for {ticker}...")

    dividend_data = client.list_dividends(
        ticker=ticker,
        limit=1000,
        order="desc",
    )

    # Safely get first dividend without consuming entire generator
    latest_dividend = get_first_dividend(dividend_data)
    if not latest_dividend:
        print(f"No dividend data found for {ticker}")
        return None

    try:
        # Check if latest dividend is too old

        # Get previous close for ex-dividend date
        ex_day = (
            datetime.strptime(latest_dividend.record_date, "%Y-%m-%d")
            - timedelta(days=1)
        ).strftime("%Y-%m-%d")

        time.sleep(12)  # Rate limiting before price check
        ex_day_data = client.get_daily_open_close_agg(
            ticker=ticker, date=ex_day, adjusted=True
        )

        # Calculate estimated yearly yield
        dividend_yield = (latest_dividend.cash_amount / ex_day_data.close) * 100
        estimate_yield_yearly = dividend_yield * latest_dividend.frequency

        print(f"Latest dividend amount: ${latest_dividend.cash_amount}")
        print(f"Stock price on {ex_day}: ${ex_day_data.close:.2f}")
        print(f"Estimated annual yield: {estimate_yield_yearly:.2f}%")

        if estimate_yield_yearly < 8:
            print(
                f"Annual yield is too low ({estimate_yield_yearly:.2f}%), skipping {ticker}"
            )
            return None

        # If yield is high enough, get all dividend data with rate limiting
        print("Yield is high enough, collecting all dividend data...")
        dividend_list = []

        # Add the first dividend we already processed
        dividend_list.append(
            {
                "ticker": latest_dividend.ticker,
                "cash_amount": latest_dividend.cash_amount,
                "currency": latest_dividend.currency,
                "declaration_date": latest_dividend.declaration_date,
                "dividend_type": latest_dividend.dividend_type,
                "ex_dividend_date": latest_dividend.ex_dividend_date,
                "frequency": latest_dividend.frequency,
                "pay_date": latest_dividend.pay_date,
                "record_date": latest_dividend.record_date,
            }
        )

        # Get rest of the dividends with rate limiting
        dividend_data = client.list_dividends(
            ticker=ticker,
            limit=1000,
            order="desc",
        )
        next(dividend_data)  # Skip the first one we already processed

        for dividend in dividend_data:
            latest_date = datetime.strptime(dividend.record_date, "%Y-%m-%d")
            cutoff_date = datetime.strptime("2014-01-01", "%Y-%m-%d")

            if latest_date < cutoff_date:
                print(
                    f"Latest dividend date {dividend.record_date} is before 2014-01-01, skipping {ticker}"
                )
                break

            dividend_list.append(
                {
                    "ticker": dividend.ticker,
                    "cash_amount": dividend.cash_amount,
                    "currency": dividend.currency,
                    "declaration_date": dividend.declaration_date,
                    "dividend_type": dividend.dividend_type,
                    "ex_dividend_date": dividend.ex_dividend_date,
                    "frequency": dividend.frequency,
                    "pay_date": dividend.pay_date,
                    "record_date": dividend.record_date,
                }
            )
            time.sleep(12)  # Rate limiting between dividend records
            print(f"Processed dividend from: {dividend.record_date}")

        # Save to JSON
        output_path = Path(f"dividend_data_{ticker}.json")
        with open(output_path, "w") as f:
            json.dump(dividend_list, f, indent=2)

        print(f"Dividend data saved to: {output_path.absolute()}")
        return dividend_list

    except Exception as e:
        print(f"Error processing dividend data: {str(e)}")
        return None


def main():
    client = RESTClient(api_key=os.getenv("POLYGON_API_KEY"))
    ticker = "HQH"

    dividend_data = check_and_save_dividend_data(client, ticker)


if __name__ == "__main__":
    main()
