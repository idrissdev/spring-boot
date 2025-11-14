#!/usr/bin/env python3
"""
Air Algerie Flight Price Scraper
Scrapes flight prices for Q1 2026 from Air Algerie's website
"""

import time
import json
import csv
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AirAlgerieFlightScraper:
    """Scraper for Air Algerie flight prices"""

    BASE_URL = "https://fly.airalgerie.dz"

    # Common routes
    ROUTES = [
        {"from": "PAR", "from_name": "Paris", "to": "AAE", "to_name": "Annaba"},
        {"from": "PAR", "from_name": "Paris", "to": "CZL", "to_name": "Constantine"},
        {"from": "PAR", "from_name": "Paris", "to": "ALG", "to_name": "Algiers"},
        {"from": "PAR", "from_name": "Paris", "to": "ORN", "to_name": "Oran"},
    ]

    FARE_CLASSES = [
        "Light",
        "Economic Promo",
        "Economic Flex",
        "Economic Smart",
        "Economic Plus"
    ]

    def __init__(self, headless: bool = False):
        """Initialize the scraper with Selenium WebDriver"""
        self.headless = headless
        self.driver = None
        self.results = []

    def setup_driver(self):
        """Setup Chrome WebDriver with options"""
        chrome_options = Options()

        if self.headless:
            chrome_options.add_argument('--headless')

        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        # Prevent detection
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        logger.info("Chrome WebDriver initialized")

    def close_driver(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            logger.info("Chrome WebDriver closed")

    def generate_date_ranges(self, start_date: datetime, end_date: datetime,
                            trip_duration: int = 3) -> List[Dict]:
        """
        Generate date ranges for Q1 2026

        Args:
            start_date: Start date for search
            end_date: End date for search
            trip_duration: Duration of trip in days

        Returns:
            List of date range dictionaries
        """
        date_ranges = []
        current = start_date

        while current <= end_date:
            departure = current
            return_date = current + timedelta(days=trip_duration)

            date_ranges.append({
                'departure': departure,
                'return': return_date
            })

            current += timedelta(days=1)

        logger.info(f"Generated {len(date_ranges)} date ranges")
        return date_ranges

    def search_flights(self, origin: str, destination: str,
                      departure_date: datetime, return_date: datetime) -> bool:
        """
        Perform flight search on Air Algerie website

        Args:
            origin: Origin airport code
            destination: Destination airport code
            departure_date: Departure date
            return_date: Return date

        Returns:
            True if search successful, False otherwise
        """
        try:
            # Navigate to Air Algerie homepage
            self.driver.get(self.BASE_URL)
            logger.info(f"Navigated to {self.BASE_URL}")

            # Wait for page to load
            time.sleep(3)

            # Fill in origin
            origin_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "booking_origin"))
            )
            origin_input.clear()
            origin_input.send_keys(origin)
            time.sleep(1)

            # Fill in destination
            dest_input = self.driver.find_element(By.ID, "booking_destination")
            dest_input.clear()
            dest_input.send_keys(destination)
            time.sleep(1)

            # Select departure date
            dep_date_input = self.driver.find_element(By.ID, "booking_date_departure")
            self.driver.execute_script(
                f"arguments[0].value = '{departure_date.strftime('%Y-%m-%d')}'",
                dep_date_input
            )

            # Select return date
            ret_date_input = self.driver.find_element(By.ID, "booking_date_return")
            self.driver.execute_script(
                f"arguments[0].value = '{return_date.strftime('%Y-%m-%d')}'",
                ret_date_input
            )

            # Submit search
            search_button = self.driver.find_element(By.ID, "booking_submit")
            search_button.click()

            # Wait for results
            time.sleep(5)

            logger.info(f"Searched for {origin} -> {destination} on {departure_date.strftime('%Y-%m-%d')}")
            return True

        except Exception as e:
            logger.error(f"Error during flight search: {e}")
            return False

    def extract_calendar_prices(self) -> List[Dict]:
        """
        Extract prices from the calendar view

        Returns:
            List of price dictionaries
        """
        prices = []

        try:
            # Find calendar dates
            calendar_days = self.driver.find_elements(By.CSS_SELECTOR, ".calendar-day")

            for day in calendar_days:
                try:
                    date_text = day.find_element(By.CSS_SELECTOR, ".date").text
                    price_elem = day.find_element(By.CSS_SELECTOR, ".price")
                    price_text = price_elem.text

                    if price_text and "€" in price_text:
                        price_value = price_text.replace("€", "").replace("from", "").strip()

                        prices.append({
                            'date': date_text,
                            'price': float(price_value.replace(",", "."))
                        })

                except NoSuchElementException:
                    continue

            logger.info(f"Extracted {len(prices)} calendar prices")

        except Exception as e:
            logger.error(f"Error extracting calendar prices: {e}")

        return prices

    def extract_flight_details(self) -> List[Dict]:
        """
        Extract detailed flight information including all fare classes

        Returns:
            List of flight detail dictionaries
        """
        flights = []

        try:
            # Find all flight rows
            flight_rows = self.driver.find_elements(By.CSS_SELECTOR, ".flight-row, .flight-item, tr.flight")

            logger.info(f"Found {len(flight_rows)} flight rows")

            for idx, row in enumerate(flight_rows):
                try:
                    flight_data = {
                        'flight_number': self._safe_extract(row, ".flight-number, .flight-code"),
                        'departure_time': self._safe_extract(row, ".departure-time, .time-departure"),
                        'arrival_time': self._safe_extract(row, ".arrival-time, .time-arrival"),
                        'duration': self._safe_extract(row, ".duration, .flight-duration"),
                        'stops': self._safe_extract(row, ".stops, .escale"),
                    }

                    # Extract fare prices
                    fare_prices = {}

                    for fare_class in self.FARE_CLASSES:
                        price = self._extract_fare_price(row, fare_class)
                        if price:
                            fare_prices[fare_class] = price

                    flight_data['fares'] = fare_prices

                    if fare_prices:  # Only add if we found prices
                        flights.append(flight_data)
                        logger.debug(f"Flight {idx+1}: {flight_data}")

                except Exception as e:
                    logger.debug(f"Error extracting flight row {idx}: {e}")
                    continue

            logger.info(f"Extracted {len(flights)} complete flight records")

        except Exception as e:
            logger.error(f"Error extracting flight details: {e}")

        return flights

    def _safe_extract(self, element, selector: str) -> Optional[str]:
        """Safely extract text from element"""
        try:
            return element.find_element(By.CSS_SELECTOR, selector).text.strip()
        except:
            return None

    def _extract_fare_price(self, element, fare_class: str) -> Optional[float]:
        """Extract price for a specific fare class"""
        try:
            # Try different selector patterns
            selectors = [
                f".fare-{fare_class.lower().replace(' ', '-')}",
                f"[data-fare='{fare_class}']",
                ".price"
            ]

            for selector in selectors:
                try:
                    price_elem = element.find_element(By.CSS_SELECTOR, selector)
                    price_text = price_elem.text

                    if "€" in price_text:
                        price_value = price_text.replace("€", "").replace(",", ".").strip()
                        # Remove any non-numeric characters except decimal point
                        price_value = ''.join(c for c in price_value if c.isdigit() or c == '.')
                        if price_value:
                            return float(price_value)
                except:
                    continue

        except Exception as e:
            logger.debug(f"Error extracting fare price for {fare_class}: {e}")

        return None

    def scrape_route(self, route: Dict, date_ranges: List[Dict]) -> List[Dict]:
        """
        Scrape all prices for a specific route across multiple dates

        Args:
            route: Route dictionary with origin and destination
            date_ranges: List of date ranges to search

        Returns:
            List of scraped results
        """
        route_results = []

        logger.info(f"Scraping route: {route['from_name']} -> {route['to_name']}")

        for idx, date_range in enumerate(date_ranges):
            try:
                logger.info(f"Searching {idx+1}/{len(date_ranges)}: {date_range['departure'].strftime('%Y-%m-%d')}")

                # Perform search
                success = self.search_flights(
                    route['from'],
                    route['to'],
                    date_range['departure'],
                    date_range['return']
                )

                if not success:
                    logger.warning(f"Search failed for {date_range['departure'].strftime('%Y-%m-%d')}")
                    continue

                # Extract prices
                flights = self.extract_flight_details()

                # Add metadata
                for flight in flights:
                    flight.update({
                        'origin': route['from'],
                        'origin_name': route['from_name'],
                        'destination': route['to'],
                        'destination_name': route['to_name'],
                        'departure_date': date_range['departure'].strftime('%Y-%m-%d'),
                        'return_date': date_range['return'].strftime('%Y-%m-%d'),
                        'scraped_at': datetime.now().isoformat()
                    })

                route_results.extend(flights)

                # Be respectful - add delay between searches
                time.sleep(2)

            except Exception as e:
                logger.error(f"Error scraping date {date_range['departure'].strftime('%Y-%m-%d')}: {e}")
                continue

        logger.info(f"Scraped {len(route_results)} results for {route['from_name']} -> {route['to_name']}")
        return route_results

    def save_results_csv(self, filename: str = "flight_prices.csv"):
        """Save results to CSV file"""
        if not self.results:
            logger.warning("No results to save")
            return

        # Flatten fare prices into columns
        csv_data = []

        for result in self.results:
            row = {
                'origin': result.get('origin'),
                'origin_name': result.get('origin_name'),
                'destination': result.get('destination'),
                'destination_name': result.get('destination_name'),
                'departure_date': result.get('departure_date'),
                'return_date': result.get('return_date'),
                'flight_number': result.get('flight_number'),
                'departure_time': result.get('departure_time'),
                'arrival_time': result.get('arrival_time'),
                'duration': result.get('duration'),
                'stops': result.get('stops'),
            }

            # Add fare prices as columns
            fares = result.get('fares', {})
            for fare_class in self.FARE_CLASSES:
                row[f'price_{fare_class.lower().replace(" ", "_")}'] = fares.get(fare_class)

            row['scraped_at'] = result.get('scraped_at')
            csv_data.append(row)

        # Write to CSV
        if csv_data:
            fieldnames = csv_data[0].keys()

            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(csv_data)

            logger.info(f"Saved {len(csv_data)} results to {filename}")

    def save_results_json(self, filename: str = "flight_prices.json"):
        """Save results to JSON file"""
        if not self.results:
            logger.warning("No results to save")
            return

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved {len(self.results)} results to {filename}")

    def run(self, routes: List[Dict] = None,
            start_date: datetime = None,
            end_date: datetime = None,
            trip_duration: int = 3):
        """
        Run the complete scraping process

        Args:
            routes: List of route dictionaries (uses defaults if None)
            start_date: Start date for searches (defaults to Jan 1, 2026)
            end_date: End date for searches (defaults to Mar 31, 2026)
            trip_duration: Trip duration in days
        """
        # Set defaults
        if routes is None:
            routes = self.ROUTES

        if start_date is None:
            start_date = datetime(2026, 1, 1)

        if end_date is None:
            end_date = datetime(2026, 3, 31)

        logger.info(f"Starting scraper for Q1 2026: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")

        try:
            # Setup driver
            self.setup_driver()

            # Generate date ranges
            date_ranges = self.generate_date_ranges(start_date, end_date, trip_duration)

            # Scrape each route
            for route in routes:
                route_results = self.scrape_route(route, date_ranges)
                self.results.extend(route_results)

            # Save results
            self.save_results_csv("flight_prices_q1_2026.csv")
            self.save_results_json("flight_prices_q1_2026.json")

            logger.info(f"Scraping complete! Total results: {len(self.results)}")

        except Exception as e:
            logger.error(f"Error during scraping: {e}")
            raise

        finally:
            self.close_driver()


def main():
    """Main entry point"""
    # Create scraper instance
    scraper = AirAlgerieFlightScraper(headless=False)

    # Define Q1 2026
    q1_start = datetime(2026, 1, 1)
    q1_end = datetime(2026, 3, 31)

    # Run scraper
    scraper.run(
        start_date=q1_start,
        end_date=q1_end,
        trip_duration=3  # 3-day trips
    )


if __name__ == "__main__":
    main()
