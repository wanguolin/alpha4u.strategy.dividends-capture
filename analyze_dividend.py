import json
import csv
from pathlib import Path
from datetime import datetime, timedelta

def calculate_dividend_yield_and_fill_gap():
    # Prepare CSV output
    output_file = Path("dividend_analysis.csv")
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = [
            'Ticker', 'Ex-Dividend Date', 'Dividend Yield (%)', 'Fill Gap Date',
            'Trading Days to Fill Gap', 'Calendar Days to Fill Gap', 'Average Daily Yield (%)'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # Iterate over each dividend data file
        for dividend_file in Path("data/").glob("dividend_data_*.json"):
            ticker_id = dividend_file.stem.split("_")[-1]
            daily_price_file = Path(f"data/daily_price_{ticker_id}.json")

            # Load dividend data
            with open(dividend_file, 'r') as f:
                dividend_data = json.load(f)

            # Load daily price data
            with open(daily_price_file, 'r') as f:
                daily_price_data = json.load(f)

            # Convert daily price data to a list of tuples (date, data) for quick lookup
            daily_price_list = [(datetime.fromtimestamp(item['timestamp'] / 1000).date(), item) for item in daily_price_data]

            for dividend in dividend_data:
                ex_dividend_date = datetime.strptime(dividend['ex_dividend_date'], "%Y-%m-%d").date()
                record_date = datetime.strptime(dividend['record_date'], "%Y-%m-%d").date()
                cash_amount = dividend['cash_amount']

                # Find the closing price on the day before the ex-dividend date
                previous_close = None
                for i, (date, data) in enumerate(daily_price_list):
                    if date == ex_dividend_date and i > 0:
                        previous_close = daily_price_list[i - 1][1]['close']
                        previous_date = datetime.fromtimestamp(daily_price_list[i - 1][1]['timestamp'] / 1000)
                        print(f"Ticker: {ticker_id}, Ex-Dividend Date: {ex_dividend_date}, Previous Trading Day: {previous_date}")
                        break

                if previous_close is None:
                    print(f"No previous trading day found for {ticker_id} on {ex_dividend_date}")
                    continue

                # Calculate dividend yield
                dividend_yield = (cash_amount / previous_close) * 100

                # Find the fill gap date (when the price recovers to the previous close)
                fill_gap_date = None
                trading_days_to_fill_gap = 0
                for date, price_data in daily_price_list:
                    if date > record_date:
                        trading_days_to_fill_gap += 1
                        if price_data['high'] > previous_close:
                            fill_gap_date = date
                            break

                # Calculate calendar days to fill gap
                calendar_days_to_fill_gap = (fill_gap_date - ex_dividend_date).days if fill_gap_date else None

                # Calculate average daily yield
                average_daily_yield = (dividend_yield / calendar_days_to_fill_gap) if calendar_days_to_fill_gap else None

                # Write to CSV
                writer.writerow({
                    'Ticker': ticker_id,
                    'Ex-Dividend Date': ex_dividend_date,
                    'Dividend Yield (%)': f"{dividend_yield:.2f}",
                    'Fill Gap Date': fill_gap_date,
                    'Trading Days to Fill Gap': trading_days_to_fill_gap if fill_gap_date else None,
                    'Calendar Days to Fill Gap': calendar_days_to_fill_gap,
                    'Average Daily Yield (%)': f"{average_daily_yield:.4f}" if average_daily_yield else None
                })

    print(f"Dividend analysis saved to: {output_file.absolute()}")

if __name__ == "__main__":
    calculate_dividend_yield_and_fill_gap()

