# config.py
import os

# Alpha Vantage API Key - Replace with your actual API key
# Get your free API key from: https://www.alphavantage.co/support/#api-key
ALPHAVANTAGE_API_KEY = os.getenv("ALPHAVANTAGE_API_KEY", "U9VMZ8EJV6H0NDP6")

# Default stock symbol
DEFAULT_SYMBOL = "AAPL"

# API settings
API_BASE_URL = "https://www.alphavantage.co/query"
REQUEST_TIMEOUT = 30  # seconds
