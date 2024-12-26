# Intorduction

This is a simple script to get the stock data from the Polygon API and save it to a CSV file.

# Installation

```bash
python3.10 -m venv .venv # prefer to use python3.10+
source .venv/bin/activate
pip install -r requirements.txt
```

# Usage

1. Create a .env file with the following variables:

```
POLYGON_API_KEY=your_api_key
IS_POLYGON_SUBSCRIBED=true
```

2. Run this script to get the major U.S. stock:

```bash
python3.10 dump_major_us_stock.py
```

3. Run this script to get the dividend data for the stocks:

```bash
python3.10 dividend_polygon.py
```

4. Run this script to analyze the dividend data:

```bash
python3.10 analyze_dividend.py
```

# Alternative

Download the data from github release.