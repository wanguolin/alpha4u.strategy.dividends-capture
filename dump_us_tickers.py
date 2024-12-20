from polygon import RESTClient
from dotenv import load_dotenv
import json
import os
from pathlib import Path
import time

load_dotenv()


def get_us_tickers(client):
    # Get all US stock exchanges
    exchanges = client.get_exchanges(asset_class="stocks", locale="us")
    exchanges_mic = [e.mic for e in exchanges if e.mic]

    print(f"Found {len(exchanges_mic)} exchanges to process")
    us_tickers = {}

    for i, exchange in enumerate(exchanges_mic, 1):
        try:
            print(f"\nProcessing exchange {exchange} ({i}/{len(exchanges_mic)})")
            # Get tickers for each exchange
            tickers = client.list_tickers(
                market="stocks", exchange=exchange, active=True, limit=1000
            )
            # Add tickers to dictionary
            ticker_count = 0
            for ticker in tickers:
                us_tickers[ticker.ticker] = False
                ticker_count += 1

            print(f"Found {ticker_count} tickers in {exchange}")
            # Rate limit: wait 12 seconds after each exchange query
            if i < len(exchanges_mic):  # Don't wait after the last exchange
                print(
                    f"Waiting 12 seconds before next request... ({i}/{len(exchanges_mic)} exchanges processed)"
                )
                time.sleep(12)

        except Exception as e:
            print(f"Error processing exchange {exchange}: {str(e)}")
            continue

    return us_tickers


def main():
    client = RESTClient(api_key=os.getenv("POLYGON_API_KEY"))

    print("Starting to fetch US tickers...")
    # Get and save tickers
    ticker_dict = get_us_tickers(client)

    # Save to JSON file
    output_path = Path("us_tickers.json")
    with open(output_path, "w") as f:
        json.dump(ticker_dict, f, indent=2)

    print(f"\nComplete!")
    print(f"Total tickers saved: {len(ticker_dict)}")
    print(f"Output saved to: {output_path.absolute()}")


if __name__ == "__main__":
    main()
