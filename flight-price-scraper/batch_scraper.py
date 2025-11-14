#!/usr/bin/env python3
"""
Batch URL Scraper for Air Algerie
Process multiple URLs from a file or list
"""

import sys
import argparse
import logging
from pathlib import Path
from airalgerie_parser import AirAlgerieParser
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('batch_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def read_urls_from_file(filepath: str) -> list:
    """Read URLs from a text file (one per line)"""
    urls = []
    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):  # Skip empty lines and comments
                    urls.append(line)
        logger.info(f"Loaded {len(urls)} URLs from {filepath}")
    except FileNotFoundError:
        logger.error(f"File not found: {filepath}")
    except Exception as e:
        logger.error(f"Error reading file: {e}")

    return urls


def scrape_batch(urls: list, output_prefix: str = "batch", headless: bool = True):
    """Scrape a batch of URLs"""
    parser = AirAlgerieParser(headless=headless)
    all_results = []
    successful = 0
    failed = 0

    try:
        total = len(urls)

        for idx, url in enumerate(urls, 1):
            logger.info(f"\n{'='*80}")
            logger.info(f"Processing URL {idx}/{total}")
            logger.info(f"{'='*80}")

            try:
                result = parser.scrape_url(url)

                if result and result.get('flights'):
                    all_results.append(result)
                    successful += 1
                    logger.info(f"✓ Successfully scraped URL {idx}: {len(result['flights'])} flights found")
                else:
                    failed += 1
                    logger.warning(f"✗ No flights found for URL {idx}")

            except Exception as e:
                failed += 1
                logger.error(f"✗ Error scraping URL {idx}: {e}")
                continue

            # Add delay between URLs to avoid overwhelming the server
            if idx < total:
                delay = 3
                logger.info(f"Waiting {delay} seconds before next URL...")
                time.sleep(delay)

        # Save results
        if all_results:
            csv_file = f"{output_prefix}_results.csv"
            json_file = f"{output_prefix}_results.json"

            parser.save_to_csv(all_results, csv_file)
            parser.save_to_json(all_results, json_file)

            logger.info(f"\n{'='*80}")
            logger.info(f"Batch Scraping Complete!")
            logger.info(f"{'='*80}")
            logger.info(f"Total URLs processed: {total}")
            logger.info(f"Successful: {successful}")
            logger.info(f"Failed: {failed}")
            logger.info(f"Total flights found: {sum(len(r.get('flights', [])) for r in all_results)}")
            logger.info(f"Results saved to:")
            logger.info(f"  - {csv_file}")
            logger.info(f"  - {json_file}")
        else:
            logger.warning("No results to save")

    finally:
        parser.close_driver()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Batch scrape Air Algerie flight prices from multiple URLs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape URLs from a file
  python batch_scraper.py urls.txt

  # Scrape with custom output prefix
  python batch_scraper.py urls.txt --output my_flights

  # Scrape in non-headless mode (show browser)
  python batch_scraper.py urls.txt --no-headless

  # Scrape specific URLs directly
  python batch_scraper.py --urls "URL1" "URL2" "URL3"
        """
    )

    parser.add_argument(
        'input_file',
        nargs='?',
        help='Text file containing URLs (one per line)'
    )

    parser.add_argument(
        '--urls',
        nargs='+',
        help='URLs to scrape (space-separated)'
    )

    parser.add_argument(
        '--output',
        default='batch',
        help='Output file prefix (default: batch)'
    )

    parser.add_argument(
        '--no-headless',
        action='store_true',
        help='Show browser window (disable headless mode)'
    )

    args = parser.parse_args()

    # Get URLs from either file or command line
    urls = []

    if args.urls:
        urls = args.urls
    elif args.input_file:
        urls = read_urls_from_file(args.input_file)
    else:
        parser.print_help()
        sys.exit(1)

    if not urls:
        logger.error("No URLs to process")
        sys.exit(1)

    # Run batch scraper
    headless = not args.no_headless
    scrape_batch(urls, output_prefix=args.output, headless=headless)


if __name__ == "__main__":
    main()
