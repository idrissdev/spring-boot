# Air Algerie Flight Price Scraper

Automated web scraper to find the best flight prices for Q1 2026 (January-March) from Air Algerie.

## Features

- ✈️ Scrapes flight prices from Air Algerie's website
- 📅 Supports date range searches across Q1 2026
- 💰 Extracts all fare classes (Light, Economic Promo, Flex, Smart, Plus)
- 🗺️ Multiple route support (Paris to various Algerian cities)
- 📊 Exports to CSV and JSON formats
- 🔄 Automatic calendar navigation
- 📸 Optional screenshot capture
- ⚡ Handles dynamic content with Selenium

## Prerequisites

### System Requirements

- Python 3.8+
- Google Chrome browser
- ChromeDriver (will be installed automatically via webdriver-manager)

### Installation

1. **Install Python dependencies:**

```bash
cd flight-price-scraper
pip install -r requirements.txt
```

Or install manually:

```bash
pip install selenium beautifulsoup4 lxml pandas requests webdriver-manager
```

2. **Verify Chrome installation:**

```bash
google-chrome --version
# or
chromium --version
```

## Usage

### Option 1: Parse Existing URLs

If you already have Air Algerie search result URLs, use the parser:

```bash
python airalgerie_parser.py
```

**Edit the URLs in `airalgerie_parser.py`:**

```python
urls = [
    "https://fly.airalgerie.dz/plnext/AirAlgerie/Override.action?...",
    "https://fly.airalgerie.dz/plnext/AirAlgerie/Override.action?...",
]
```

### Option 2: Full Automated Search

Use the full scraper to perform automated searches:

```bash
python airalgerie_scraper.py
```

**Customize in `config.json`:**

```json
{
  "search_parameters": {
    "start_date": "2026-01-01",
    "end_date": "2026-03-31",
    "trip_duration_days": 3
  },
  "routes": [
    {
      "name": "Paris to Annaba",
      "origin": "PAR",
      "destination": "AAE"
    }
  ]
}
```

### Option 3: Batch URL Processing

Process multiple URLs from a file:

```bash
python batch_scraper.py urls.txt
```

Create `urls.txt` with one URL per line.

## Configuration

Edit `config.json` to customize:

### Search Parameters

- **start_date**: Start date for searches (YYYY-MM-DD)
- **end_date**: End date for searches (YYYY-MM-DD)
- **trip_duration_days**: Trip length in days

### Routes

Add or modify routes:

```json
{
  "name": "Route Name",
  "origin": "ORIGIN_CODE",
  "destination": "DEST_CODE",
  "origin_full": "Origin Airport Full Name",
  "destination_full": "Destination Airport Full Name"
}
```

**Common Airport Codes:**

- **Paris:** PAR (all airports), CDG (Charles de Gaulle), ORY (Orly)
- **Algeria:**
  - AAE - Annaba (Rabah Bitat)
  - ALG - Algiers (Houari Boumediene)
  - CZL - Constantine (Mohamed Boudiaf)
  - ORN - Oran (Ahmed Ben Bella)
  - TLM - Tlemcen (Zenata)
  - BJA - Bejaia (Soummam)

### Scraper Settings

- **headless**: Run browser in headless mode (true/false)
- **delay_between_searches**: Delay in seconds between searches
- **max_retries**: Maximum retry attempts for failed requests
- **timeout**: Page load timeout in seconds
- **save_screenshots**: Save screenshots of each page (true/false)

## Output

The scraper generates two output files:

### 1. CSV File (`airalgerie_prices_q1_2026.csv`)

Structured data with columns:
- Route information (origin, destination)
- Flight details (number, times, duration, stops)
- Fare prices for each class
- Timestamp

Example:

```csv
origin,destination,departure_date,flight_number,price_light,price_economic_promo,price_economic_flex
PAR,AAE,2026-01-15,AH1545,99.60,134.60,329.60
```

### 2. JSON File (`airalgerie_prices_q1_2026.json`)

Complete structured data including:
- Calendar prices
- Flight details
- Fare breakdowns
- Metadata

## How It Works

### 1. Parser Approach (`airalgerie_parser.py`)

For direct URL scraping:

1. Loads the provided URL using Selenium
2. Waits for page to fully render
3. Parses HTML with BeautifulSoup
4. Extracts:
   - Calendar date prices
   - Flight details (times, duration, stops)
   - All fare class prices
5. Navigates through calendar (+7 days) to collect extended data
6. Saves to CSV and JSON

### 2. Full Scraper Approach (`airalgerie_scraper.py`)

For automated searching:

1. Reads configuration from `config.json`
2. Generates date ranges for Q1 2026
3. For each route and date:
   - Navigates to Air Algerie homepage
   - Fills in search form
   - Submits search
   - Extracts prices
4. Saves all results to files

## Fare Classes

The scraper extracts prices for all available fare classes:

| Fare Class | Refundable | Changeable | Checked Baggage |
|------------|------------|------------|-----------------|
| **Light** | No | With fees | No luggage |
| **Economic Promo** | No | With fees | 1 x 23kg |
| **Economic Flex** | Partial (fees) | With fees | 1 x 23kg |
| **Economic Smart** | Partial (fees) | Free | 1 x 23kg |
| **Economic Plus** | Yes (free) | Free | 1 x 23kg |

## Tips for Best Results

1. **Run during off-peak hours**: Less website traffic means faster scraping
2. **Use headless mode**: Set `"headless": true` for faster execution
3. **Adjust delays**: Increase `delay_between_searches` if getting blocked
4. **Start small**: Test with a single route and short date range first
5. **Save screenshots**: Enable for debugging if scraping fails

## Troubleshooting

### Chrome/ChromeDriver Issues

```bash
# Install ChromeDriver manager
pip install webdriver-manager

# Or manually download ChromeDriver
# Download from: https://chromedriver.chromium.org/
```

### Page Not Loading

- Increase timeout in config.json
- Disable headless mode to see what's happening
- Check your internet connection
- Verify the Air Algerie website is accessible

### No Prices Found

- The website structure may have changed
- Enable `save_screenshots` to see what's being loaded
- Check logs for specific error messages
- Try running without headless mode

### Session Timeout

Air Algerie URLs contain session IDs that expire. If using saved URLs:

1. Generate fresh URLs by performing manual searches
2. Use them immediately
3. Or use the full automated scraper instead

## Examples

### Example 1: Scrape Specific Dates

```python
from airalgerie_parser import AirAlgerieParser
from datetime import datetime

parser = AirAlgerieParser(headless=True)
result = parser.scrape_url("YOUR_AIR_ALGERIE_URL_HERE")

print(f"Found {len(result['flights'])} flights")
print(f"Calendar prices: {result['calendar_prices']}")

parser.close_driver()
```

### Example 2: Search Multiple Routes

Edit `config.json` to include your routes, then:

```bash
python airalgerie_scraper.py
```

### Example 3: Find Cheapest Flights

After scraping, analyze the CSV:

```python
import pandas as pd

df = pd.read_csv('airalgerie_prices_q1_2026.csv')

# Find cheapest Economic Promo flights
cheapest = df.nsmallest(10, 'price_economic_promo')
print(cheapest[['origin', 'destination', 'departure_date', 'price_economic_promo']])
```

## Best Practices

1. **Respect the website**: Don't scrape too aggressively
2. **Add delays**: Use reasonable delays between requests
3. **Error handling**: The scraper includes retry logic
4. **Data validation**: Review results for accuracy
5. **Regular updates**: Website structure may change over time

## Data Analysis

Once you have the data, you can:

1. **Find cheapest dates**: Identify low-price periods
2. **Compare routes**: See which routes offer best value
3. **Track trends**: Monitor price changes over time
4. **Optimize bookings**: Find the best fare class for your needs

Example analysis:

```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('airalgerie_prices_q1_2026.csv')

# Plot prices over time
df['departure_date'] = pd.to_datetime(df['departure_date'])
df.groupby('departure_date')['price_economic_promo'].min().plot()
plt.title('Minimum Flight Prices - Q1 2026')
plt.xlabel('Date')
plt.ylabel('Price (€)')
plt.show()
```

## Legal & Ethical Considerations

- ⚠️ Web scraping may violate Air Algerie's Terms of Service
- 📋 This tool is for personal research and education only
- 🚫 Do not use for commercial purposes without permission
- 🤝 Respect the website's robots.txt
- ⏱️ Use reasonable rate limiting

## License

This project is provided as-is for educational purposes.

## Contributing

Feel free to submit issues or improvements!

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the logs in `scraper.log`
3. Enable screenshots to debug visually

---

**Happy flight hunting! ✈️**
