#!/usr/bin/env python3
"""
Air Algerie HTML Parser
Parses flight price data from Air Algerie search results pages
"""

import re
import json
import csv
from datetime import datetime
from typing import List, Dict, Optional
import logging
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AirAlgerieParser:
    """Parse Air Algerie flight search results"""

    FARE_CLASSES = {
        'Light': 'light',
        'Economic Promo': 'economic_promo',
        'Economique Promo': 'economic_promo',
        'Economic Flex': 'economic_flex',
        'Economique Flex': 'economic_flex',
        'Economic Smart': 'economic_smart',
        'Economique Smart': 'economic_smart',
        'Economic Plus': 'economic_plus',
        'Economique Plus': 'economic_plus'
    }

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver = None
        self.results = []

    def setup_driver(self):
        """Setup Chrome WebDriver"""
        chrome_options = Options()

        if self.headless:
            chrome_options.add_argument('--headless')

        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

        self.driver = webdriver.Chrome(options=chrome_options)
        logger.info("WebDriver initialized")

    def close_driver(self):
        """Close WebDriver"""
        if self.driver:
            self.driver.quit()

    def extract_price(self, text: str) -> Optional[float]:
        """Extract price value from text"""
        if not text:
            return None

        # Remove common price prefixes
        text = text.replace('from', '').replace('à partir de', '').replace('€', '').strip()

        # Try to extract numeric value
        match = re.search(r'(\d+[.,]\d+)', text)
        if match:
            price_str = match.group(1).replace(',', '.')
            try:
                return float(price_str)
            except ValueError:
                pass

        return None

    def parse_calendar_dates(self, html: str) -> List[Dict]:
        """Parse calendar dates and prices"""
        soup = BeautifulSoup(html, 'lxml')
        calendar_prices = []

        try:
            # Find calendar day elements
            # The user's example shows dates like "Sat 06", "Sun 07", etc.
            calendar_items = soup.find_all(['div', 'td', 'li'], class_=re.compile(r'(calendar|day|date)', re.I))

            for item in calendar_items:
                date_text = None
                price_text = None

                # Try to find date
                date_elem = item.find(['span', 'div', 'strong'], class_=re.compile(r'date', re.I))
                if date_elem:
                    date_text = date_elem.get_text(strip=True)
                else:
                    # Check if the text contains a date pattern
                    text = item.get_text(strip=True)
                    if re.search(r'\d{2}', text):
                        date_text = text

                # Try to find price
                price_elem = item.find(text=re.compile(r'€'))
                if price_elem:
                    price_text = price_elem.strip()
                    price = self.extract_price(price_text)

                    if price and date_text:
                        calendar_prices.append({
                            'date': date_text,
                            'price': price
                        })

            logger.info(f"Found {len(calendar_prices)} calendar prices")

        except Exception as e:
            logger.error(f"Error parsing calendar: {e}")

        return calendar_prices

    def parse_flight_list(self, html: str) -> List[Dict]:
        """Parse flight list from search results"""
        soup = BeautifulSoup(html, 'lxml')
        flights = []

        try:
            # Find all flight containers
            # Look for common flight row patterns
            flight_containers = soup.find_all(['div', 'tr'], class_=re.compile(r'flight', re.I))

            logger.info(f"Found {len(flight_containers)} potential flight containers")

            for idx, container in enumerate(flight_containers):
                try:
                    flight_data = self._parse_flight_container(container)
                    if flight_data and flight_data.get('fares'):
                        flights.append(flight_data)
                        logger.debug(f"Parsed flight {idx + 1}: {flight_data.get('flight_number', 'Unknown')}")
                except Exception as e:
                    logger.debug(f"Error parsing flight container {idx}: {e}")

        except Exception as e:
            logger.error(f"Error parsing flight list: {e}")

        return flights

    def _parse_flight_container(self, container) -> Optional[Dict]:
        """Parse individual flight container"""
        flight_data = {}

        # Extract flight times
        times = container.find_all(text=re.compile(r'\d{2}:\d{2}'))
        if len(times) >= 2:
            flight_data['departure_time'] = times[0].strip()
            flight_data['arrival_time'] = times[1].strip()

        # Extract airport codes
        airports = container.find_all(['span', 'div'], class_=re.compile(r'(airport|code)', re.I))
        if len(airports) >= 2:
            flight_data['origin'] = airports[0].get_text(strip=True)
            flight_data['destination'] = airports[1].get_text(strip=True)

        # Extract duration
        duration = container.find(text=re.compile(r'Durée|Duration|Dur[eé]e|h\d+m', re.I))
        if duration:
            flight_data['duration'] = duration.strip()

        # Extract stops
        stops = container.find(text=re.compile(r'Direct|escale|stop', re.I))
        if stops:
            flight_data['stops'] = stops.strip()

        # Extract flight number (format: AH1234)
        flight_num = container.find(text=re.compile(r'AH\d+|Air Algerie \(\w+\d+\)', re.I))
        if flight_num:
            match = re.search(r'AH\d+', flight_num)
            if match:
                flight_data['flight_number'] = match.group(0)

        # Extract all fare prices
        fares = self._extract_fares_from_container(container)
        flight_data['fares'] = fares

        return flight_data if fares else None

    def _extract_fares_from_container(self, container) -> Dict[str, float]:
        """Extract all fare class prices from container"""
        fares = {}

        # Find all price elements
        price_elements = container.find_all(text=re.compile(r'€\s*\d+'))

        # Also look for fare class labels
        fare_labels = container.find_all(text=re.compile(r'Light|Economic|Economique', re.I))

        # Try to match fare classes with prices
        for label_elem in fare_labels:
            label = label_elem.strip()

            # Find the corresponding price
            # Look for price in the same parent or nearby elements
            parent = label_elem.parent
            if parent:
                price_elem = parent.find(text=re.compile(r'€'))
                if price_elem:
                    price = self.extract_price(price_elem)
                    if price:
                        # Normalize fare class name
                        for key, normalized in self.FARE_CLASSES.items():
                            if key.lower() in label.lower():
                                fares[key] = price
                                break

        # Alternative: look for structured fare sections
        fare_sections = container.find_all(['div', 'td'], class_=re.compile(r'fare|price|tarif', re.I))
        for section in fare_sections:
            label = section.get('data-fare') or section.get('class')
            price_text = section.get_text(strip=True)
            price = self.extract_price(price_text)

            if price and label:
                for key, normalized in self.FARE_CLASSES.items():
                    if normalized in str(label).lower():
                        fares[key] = price
                        break

        return fares

    def scrape_url(self, url: str) -> Dict:
        """Scrape a single URL using Selenium"""
        result = {
            'url': url,
            'calendar_prices': [],
            'flights': [],
            'scraped_at': datetime.now().isoformat()
        }

        try:
            if not self.driver:
                self.setup_driver()

            logger.info(f"Loading URL: {url[:100]}...")
            self.driver.get(url)

            # Wait for page to load
            time.sleep(5)

            # Try to wait for flight results
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "flight"))
                )
            except:
                logger.warning("Could not find flight elements with class 'flight'")

            # Get page source
            html = self.driver.page_source

            # Parse route info from page
            result['route_info'] = self._extract_route_info(html)

            # Parse calendar prices
            result['calendar_prices'] = self.parse_calendar_dates(html)

            # Parse flight list
            result['flights'] = self.parse_flight_list(html)

            # Try to click through calendar dates to get more prices
            result['extended_calendar'] = self._navigate_calendar()

            logger.info(f"Scraped {len(result['flights'])} flights and {len(result['calendar_prices'])} calendar prices")

        except Exception as e:
            logger.error(f"Error scraping URL: {e}")

        return result

    def _extract_route_info(self, html: str) -> Dict:
        """Extract route information from page"""
        soup = BeautifulSoup(html, 'lxml')
        info = {}

        try:
            # Look for route info in heading or search summary
            route_text = soup.find(text=re.compile(r'Paris.*to|Paris.*À', re.I))
            if route_text:
                info['route_description'] = route_text.strip()

            # Extract dates
            date_text = soup.find(text=re.compile(r'(Jan|Feb|Mar|Janv|Févr|Mars).*\d{4}', re.I))
            if date_text:
                info['search_dates'] = date_text.strip()

        except Exception as e:
            logger.debug(f"Error extracting route info: {e}")

        return info

    def _navigate_calendar(self) -> List[Dict]:
        """Navigate through calendar to collect more prices"""
        extended_prices = []

        try:
            # Look for "next 7 days" button
            next_buttons = self.driver.find_elements(By.XPATH,
                "//*[contains(text(), '+7') or contains(text(), 'next') or contains(text(), 'suivant')]")

            for _ in range(12):  # Navigate through ~3 months
                if next_buttons:
                    try:
                        next_buttons[0].click()
                        time.sleep(2)

                        # Parse new calendar prices
                        html = self.driver.page_source
                        prices = self.parse_calendar_dates(html)
                        extended_prices.extend(prices)

                        # Find next button again (page may have refreshed)
                        next_buttons = self.driver.find_elements(By.XPATH,
                            "//*[contains(text(), '+7') or contains(text(), 'next') or contains(text(), 'suivant')]")
                    except:
                        break
                else:
                    break

            logger.info(f"Collected {len(extended_prices)} extended calendar prices")

        except Exception as e:
            logger.debug(f"Error navigating calendar: {e}")

        return extended_prices

    def save_to_csv(self, results: List[Dict], filename: str = "flight_prices.csv"):
        """Save results to CSV"""
        rows = []

        for result in results:
            base_info = {
                'url': result.get('url'),
                'route': result.get('route_info', {}).get('route_description', ''),
                'search_dates': result.get('route_info', {}).get('search_dates', ''),
                'scraped_at': result.get('scraped_at')
            }

            # Add flight data
            for flight in result.get('flights', []):
                row = base_info.copy()
                row.update({
                    'flight_number': flight.get('flight_number'),
                    'departure_time': flight.get('departure_time'),
                    'arrival_time': flight.get('arrival_time'),
                    'duration': flight.get('duration'),
                    'stops': flight.get('stops'),
                })

                # Add fare prices
                for fare_class, price in flight.get('fares', {}).items():
                    row[f'price_{fare_class.lower().replace(" ", "_")}'] = price

                rows.append(row)

        if rows:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)

            logger.info(f"Saved {len(rows)} rows to {filename}")

    def save_to_json(self, results: List[Dict], filename: str = "flight_prices.json"):
        """Save results to JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved results to {filename}")


def main():
    """Main entry point"""
    # Example URLs from user
    urls = [
        # Paris -> Annaba (example from user)
        "https://fly.airalgerie.dz/plnext/AirAlgerie/Override.action;jsessionid=aF4Ee6AwH-TREPEsZFKpT98VstdYTRo2ItzQqGH1!1763137544642?BOOKING_FLOW=REVENUE&COUNTRY_SITE=GB&EMBEDDED_TRANSACTION=FlexPricerAvailability&ENC=35f680e7f1f36177444bf365b6c9b5bb6944e2e9bdc6e275e7d7123df98374681a62872eca90b2ef1f2c84e7c86424cae5d88fca610a135fb85e9e44b85196445af39e52dd84f550e02c325ac595bf792d0398eed172de62deae186304c006b038e4003131fa60a0de9b5f7f10192bc9f733ab52915e1afca2ad48e53963f0cbb4bad3163557ceea613b82794ed11a7e9d8c480377645e8194cd3d64528f347ee635a965ae5039b0c78224c59929ae872863136c86e300c2efe04a37a49387253fdaf27dd9f41d0c093fe3d5ed81d9bd624ada13b0733e0ba856ca97cc23bf01f8333cf7a801ed628336862754d7522eff6c9696eb012cae21de1bbc66d3280ee016b79b17f596e3280d1c4c7b5efacb3a67540efcd85d8d28c0ddad34788e5904c31daa220f4697da6545c1f95f44180faa517eb9aadc19ce927a250528494724269159a7b79ea08b6d6d5fb76eb88442a4eec6d436b899476e846c115d0713c1f4c6fe9b1feda1b62608b6ef629982217d781940c28680f69f20f0736eb625637621e11c8a2d2fe33bb6ec53dc7a87db3221b3a1ed82bb9b23beebda771e76f734eed50b785326ac8c000b5983ff42daefa7c9fb40f0a3067f808883c9560f3bd61322a1556bb2184db63c23f6156dcc5be33bd08e27820d33797b1d8a21379813becfc1ba7834bae2e7ffbbf897f6b781d41d0adfda537237a577e467c255800e852075ec02fd43de75e6a59dde99af749a102eae5a357bdda8b64c926e405dc652dce4dce59f87ec53e54f9bd5e743f7beb3c8d2f5b0066002849651d6c9718c39df8baea2b19ecde18c19da99e71952777e74bb09bb08ee42754388b529ff2bc13496feb934614d6db72d62ab91c5f90fcb3f511dc8810efd9aae1903c6bd86da80d4ea6064ea9d22dde0b11b2b562d17970fdfbbc09c5b79a3a2c68796e30e0cc274c12f4c7ae21146d83febfb4ebd543a61180f58f44165ee7c2ffe758541958166380a8b6a14fde3f2db4f56218e395f0c860a3dfbb55fb9dcc8316598aa1fdd41097fad25470daf85c8fec50f4afcbb01cdbdb77d54bd1969b9a2e219870bcc46745a5361114d93afed3c58d9521763c616d26fbc6471aa2318cf35277aae567ff8a1da5edb4373ede50ea4ab4bc6bd16dd6edc4f3357c73d89a4fd24c644d264166a505d316cc07f3c41304c7a9498def0157b6843b3d904f5b1cc32b9e763ea23f1e7f1fc04e364a662e5a6ab0471495bb7180cd1114e5093a32ad69413a1697c722cb3fe52b109b0596964d978db8edbf468b8b88498357d9389e104a8b7e943eeeffb35dfb2fff3a7e7a73ec46ff2cb5b98480ae8e8603ca6ce&ENCT=1&EXTERNAL_ID=BOOKING&LANGUAGE=GB&OFFICE_ID=ALGAH08AA&PAGE_ID=FPOW&SITE=P02IP02I&TRIP_FLOW=YES&_t=1763137548&force_device=",

        # Paris -> Constantine (example from user)
        "https://fly.airalgerie.dz/plnext/AirAlgerie/Override.action;jsessionid=QiytaWrc2W26vJtNAkc88-RuSmJmY0cnjR5C5nLA!1763138685052?BOOKING_FLOW=REVENUE&COUNTRY_SITE=GB&EMBEDDED_TRANSACTION=FlexPricerAvailability&ENC=35f680e7f1f36177444bf365b6c9b5bb6944e2e9bdc6e275e7d7123df98374681a62872eca90b2ef1f2c84e7c86424cae5d88fca610a135fb85e9e44b85196445af39e52dd84f550e02c325ac595bf79abde63784969dcc307c15be13d09c684cd8fdea7c4ae258652f86c2dcdb7b01ef733ab52915e1afca2ad48e53963f0cb0d531b425ab4a63af7300ce0426728d1afde2a63a3f32db143fe1dc56e79964fe635a965ae5039b0c78224c59929ae872863136c86e300c2efe04a37a49387253fdaf27dd9f41d0c093fe3d5ed81d9bd624ada13b0733e0ba856ca97cc23bf019da466759872e43132e4e903404e8fc4ff6c9696eb012cae21de1bbc66d3280ead5a4105cbf7ce497e00711930518abb2b724222181ea0968ee7b86f4408c7dc04c31daa220f4697da6545c1f95f44180faa517eb9aadc19ce927a250528494724269159a7b79ea08b6d6d5fb76eb88442a4eec6d436b899476e846c115d0713c1f4c6fe9b1feda1b62608b6ef629982217d781940c28680f69f20f0736eb625637621e11c8a2d2fe33bb6ec53dc7a87db3221b3a1ed82bb9b23beebda771e76f734eed50b785326ac8c000b5983ff42daefa7c9fb40f0a3067f808883c9560f3bd61322a1556bb2184db63c23f6156dcc5be33bd08e27820d33797b1d8a21379813becfc1ba7834bae2e7ffbbf897f6b781d41d0adfda537237a577e467c255c4f756fa40a281109f0a7a8ad7476664ae6abeea6f39c375c761f42eeebebc3920212f78c92d18795ae7f03022b378102493144029cfb3d71b2f9705993c4397c0a5c7f4bbe533eba6ad95d096350fc719870bcc46745a5361114d93afed3c58adf4fce58a1e4731025e6babdec27f25277aae567ff8a1da5edb4373ede50ea437dbcd6cf288abb85e672652e6f2f3c149afef436efbea3ff6daae0bfee72fc77e76f0caf8f12f50cd990d08da5e44f2c99867f67b188c50cd3ff8fbf535cd015889bcda775ca5362080c1b9ca339f78e8f91712f89fbd6651e409dbc2fb66e68728c4f6e9da4bc12a2bed4fa732f6e5209c9d2eafbadbb1fd424b933fcd0a9eb92bb045df312609c581585de8108f74c9d9a3c9999299206c1ca6d7cf5de723955ca484460abece87abc39466a300a3ed9c9a8ba3bd400d9f5ef40b87459989934f506a1e3556c5a11c68dc6df026e1de022f4d81c8a54d8d37be06efb26b55b5a5db1b8bc94b5c20667267135fb675170ffaa0cb243b07c840e853c0196d4ef185e74fe0919253e85d13436a4785b922c3498a74edb4b50d5e3ca43c4e69e95409d50cd815685f3d43b0b85e8965dbfcf4c315c8f1cceae81a5cc0e91f03f0&ENCT=1&EXTERNAL_ID=BOOKING&LANGUAGE=FR&OFFICE_ID=ALGAH08AA&PAGE_ID=FPOW&SITE=P02IP02I&TRIP_FLOW=YES&_t=1763138687&force_device="
    ]

    parser = AirAlgerieParser(headless=False)

    try:
        all_results = []

        for url in urls:
            logger.info(f"\n{'='*80}\nScraping URL {len(all_results)+1}/{len(urls)}\n{'='*80}")
            result = parser.scrape_url(url)
            all_results.append(result)

            # Add delay between URLs
            time.sleep(3)

        # Save results
        parser.save_to_csv(all_results, "airalgerie_prices_q1_2026.csv")
        parser.save_to_json(all_results, "airalgerie_prices_q1_2026.json")

        # Summary
        total_flights = sum(len(r.get('flights', [])) for r in all_results)
        logger.info(f"\n{'='*80}\nScraping Complete!\n{'='*80}")
        logger.info(f"Total URLs scraped: {len(all_results)}")
        logger.info(f"Total flights found: {total_flights}")

    finally:
        parser.close_driver()


if __name__ == "__main__":
    main()
