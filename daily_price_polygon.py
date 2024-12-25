from polygon import RESTClient
from datetime import datetime
import os
import json
from pathlib import Path
import dotenv

dotenv.load_dotenv()

# Initialize the REST client
client = RESTClient(api_key=os.getenv("POLYGON_API_KEY"))

# Get the current year and calculate the start date (five years ago, January 1st)
current_year = datetime.now().year
start_date = datetime(current_year - 5, 1, 1)
end_date = datetime.now()

# Iterate over each file in the "data" directory that starts with "dividend_data_"
for file in Path("data/").glob("dividend_data_*.json"):
    # Extract the ticker ID from the file name
    ticker_id = file.stem.split("_")[-1]

    # Fetch daily aggregate data for the ticker
    ticker_daily = client.get_aggs(
        ticker=ticker_id,
        multiplier=1,
        timespan="day",
        from_=start_date.strftime("%Y-%m-%d"),
        to=end_date.strftime("%Y-%m-%d"),
        adjusted=False
    )

    # Save the fetched data to a JSON file
    output_path = Path(f"data/daily_price_{ticker_id}.json")
    with open(output_path, "w") as f:
        json.dump([agg.__dict__ for agg in ticker_daily], f, indent=2)

    print(f"Daily price data for {ticker_id} saved to: {output_path.absolute()}")
