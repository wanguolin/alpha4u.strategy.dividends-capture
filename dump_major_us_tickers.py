from polygon import RESTClient
from dotenv import load_dotenv
import json
import os
from pathlib import Path
import time

load_dotenv()

def sleep_if_not_subscribed():
    if not os.getenv("IS_POLYGON_SUBSCRIBED"):
        time.sleep(12)

def get_us_tickers(client):
    major_exchanges = ['XNYS', 'XNAS', 'XASE']
    print(f"Processing {len(major_exchanges)} major exchanges")
    all_tickers = []

    for i, exchange in enumerate(major_exchanges, 1):
        try:
            print(f"\nProcessing exchange {exchange} ({i}/{len(major_exchanges)})")
            tickers = client.list_tickers(
                market="stocks", 
                exchange=exchange, 
                active=True,
            )
            
            # Convert iterator to list and collect all results
            exchange_tickers = list(tickers)
            all_tickers.extend(exchange_tickers)
            
            print(f"Found {len(exchange_tickers)} tickers in {exchange}")
            if i < len(major_exchanges):
                sleep_if_not_subscribed()
        except Exception as e:
            print(f"Error processing exchange {exchange}: {str(e)}")
            continue

    return all_tickers


def main():
    client = RESTClient(api_key=os.getenv("POLYGON_API_KEY"))

    print("Starting to fetch US tickers...")
    # Get tickers
    tickers = get_us_tickers(client)

    # Save to JSON file
    output_path = Path("us_major_tickers.json")
    with open(output_path, "w") as f:
        json.dump(tickers, f, indent=2, default=lambda x: x.__dict__)

    print(f"\nComplete!")
    print(f"Total tickers saved: {len(tickers)}")
    print(f"Output saved to: {output_path.absolute()}")


if __name__ == "__main__":
    main()
