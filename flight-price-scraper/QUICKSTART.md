# Quick Start Guide

## Installation (2 minutes)

```bash
cd flight-price-scraper

# Run the setup script
bash quickstart.sh

# Or manually:
pip install -r requirements.txt
```

## Test Your Setup

```bash
python3 test_setup.py
```

## Usage

### Option 1: Parse Your URLs (Easiest) ⭐

1. **Get fresh URLs from Air Algerie:**
   - Visit https://fly.airalgerie.dz
   - Search for flights (Paris → Annaba, Constantine, etc.)
   - Copy the full URL from your browser

2. **Add URLs to a file:**
   ```bash
   # Edit example_urls.txt or create your own
   nano my_urls.txt
   # Paste your URLs, one per line
   ```

3. **Run the scraper:**
   ```bash
   python3 batch_scraper.py my_urls.txt
   ```

4. **Results:**
   - `batch_results.csv` - Spreadsheet format
   - `batch_results.json` - Raw data

### Option 2: Use Example URLs

```bash
# Scrape the provided example URLs
python3 airalgerie_parser.py
```

**Note:** Example URLs may expire (session timeout). Get fresh URLs if they don't work.

### Option 3: Automated Search (Advanced)

```bash
# Edit config.json to set routes and dates
python3 airalgerie_scraper.py
```

## Analyze Results

```bash
# Generate full report
python3 analyze_prices.py --report

# Find 20 cheapest flights
python3 analyze_prices.py --cheapest 20

# Export deals under €150
python3 analyze_prices.py --export-deals 150

# Find best dates for Paris → Annaba
python3 analyze_prices.py --best-dates PAR AAE
```

## Typical Workflow

```bash
# 1. Setup (once)
bash quickstart.sh

# 2. Get fresh URLs from Air Algerie website
#    (manually search and copy URLs)

# 3. Create URL file
cat > my_urls.txt << EOF
https://fly.airalgerie.dz/plnext/AirAlgerie/Override.action?...
https://fly.airalgerie.dz/plnext/AirAlgerie/Override.action?...
EOF

# 4. Scrape
python3 batch_scraper.py my_urls.txt

# 5. Analyze
python3 analyze_prices.py --cheapest 10

# 6. Open results
# CSV can be opened in Excel, Google Sheets, etc.
```

## Tips

- **Fresh URLs**: Air Algerie URLs expire after ~30 minutes. Generate new ones if scraping fails.
- **Browser visible**: Use `--no-headless` to see what's happening
- **Multiple routes**: Search for different routes and add all URLs to your file
- **Q1 2026**: Use the calendar navigation (+7 days) to explore Jan-Mar 2026

## Common Issues

### "No flights found"
- URLs may have expired - get fresh ones
- Try with `--no-headless` to see the browser

### "ChromeDriver not found"
```bash
pip install webdriver-manager
```

### "Module not found"
```bash
pip install -r requirements.txt
```

## File Outputs

- `*_results.csv` - Spreadsheet with all flight data
- `*_results.json` - Raw JSON data
- `*.log` - Execution logs

## Next Steps

See [README.md](README.md) for detailed documentation.
