#!/usr/bin/env python3
"""
Demo: Air Algerie Flight Price Parser
Simplified version that works without Selenium browser
Uses requests + BeautifulSoup to parse HTML directly
"""

import re
import json
import csv
from datetime import datetime
from typing import List, Dict, Optional
import logging

try:
    from bs4 import BeautifulSoup
    import requests
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.run(["pip", "install", "-q", "beautifulsoup4", "lxml", "requests"])
    from bs4 import BeautifulSoup
    import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SimpleFlightParser:
    """Simple parser that works without Selenium"""

    def __init__(self):
        self.results = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def extract_price(self, text: str) -> Optional[float]:
        """Extract price from text"""
        if not text:
            return None

        text = text.replace('€', '').replace(',', '.').strip()
        match = re.search(r'(\d+\.?\d*)', text)
        if match:
            try:
                return float(match.group(1))
            except:
                pass
        return None

    def parse_html(self, html: str, url: str) -> Dict:
        """Parse flight data from HTML"""
        soup = BeautifulSoup(html, 'lxml')
        result = {
            'url': url,
            'scraped_at': datetime.now().isoformat(),
            'flights': [],
            'calendar_prices': []
        }

        # Extract route info
        route_info = self._extract_route_info(soup)
        result['route'] = route_info

        # Find all prices on the page
        prices = self._extract_all_prices(soup)
        result['all_prices'] = prices

        # Try to extract structured flight data
        flights = self._extract_flights(soup)
        result['flights'] = flights

        return result

    def _extract_route_info(self, soup) -> Dict:
        """Extract route information"""
        info = {}

        # Look for origin/destination
        text = soup.get_text()

        # Extract dates
        date_match = re.search(r'(\d{1,2}\s+(?:Jan|Feb|Mar|Janv|Févr|Mars))', text, re.I)
        if date_match:
            info['date'] = date_match.group(1)

        # Extract cities
        city_patterns = [
            r'Paris.*?to\s+(\w+)',
            r'Paris.*?À\s+(\w+)',
            r'From.*?Paris.*?to\s+(\w+)',
        ]

        for pattern in city_patterns:
            match = re.search(pattern, text, re.I | re.DOTALL)
            if match:
                info['destination'] = match.group(1)
                info['origin'] = 'Paris'
                break

        return info

    def _extract_all_prices(self, soup) -> List[float]:
        """Extract all price values from page"""
        prices = []

        # Find all text containing €
        price_texts = soup.find_all(text=re.compile(r'€\s*\d+'))

        for text in price_texts:
            price = self.extract_price(text)
            if price and price > 0:
                prices.append(price)

        return sorted(set(prices))

    def _extract_flights(self, soup) -> List[Dict]:
        """Extract flight information"""
        flights = []

        # Look for time patterns (HH:MM)
        times = soup.find_all(text=re.compile(r'\d{2}:\d{2}'))
        times = [t.strip() for t in times if re.match(r'^\d{2}:\d{2}$', t.strip())]

        # Look for flight numbers (AH followed by digits)
        flight_nums = soup.find_all(text=re.compile(r'AH\d+'))
        flight_nums = [f.strip() for f in flight_nums]

        # Look for prices
        price_elements = soup.find_all(text=re.compile(r'€'))

        logger.info(f"Found {len(times)} times, {len(flight_nums)} flight numbers")

        # Try to group into flights (pairs of times = departure/arrival)
        for i in range(0, len(times)-1, 2):
            flight = {
                'departure_time': times[i],
                'arrival_time': times[i+1] if i+1 < len(times) else None,
                'flight_number': flight_nums[i//2] if i//2 < len(flight_nums) else None,
            }
            flights.append(flight)

        return flights

    def fetch_and_parse(self, url: str) -> Dict:
        """Fetch URL and parse"""
        logger.info(f"Fetching: {url[:80]}...")

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            logger.info(f"Received {len(response.content)} bytes")

            result = self.parse_html(response.text, url)
            self.results.append(result)

            return result

        except Exception as e:
            logger.error(f"Error fetching URL: {e}")
            return {
                'url': url,
                'error': str(e),
                'scraped_at': datetime.now().isoformat()
            }

    def save_results(self, filename_prefix='demo'):
        """Save results to files"""

        # Save JSON
        json_file = f"{filename_prefix}_results.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved to {json_file}")

        # Create summary CSV
        csv_file = f"{filename_prefix}_summary.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Route', 'Date', 'Min Price (€)', 'Max Price (€)', 'Avg Price (€)', 'Flights Found', 'Unique Prices'])

            for result in self.results:
                route = result.get('route', {})
                origin = route.get('origin', 'N/A')
                dest = route.get('destination', 'N/A')
                date = route.get('date', 'N/A')

                prices = result.get('all_prices', [])
                flights = result.get('flights', [])

                if prices:
                    writer.writerow([
                        f"{origin} → {dest}",
                        date,
                        f"{min(prices):.2f}",
                        f"{max(prices):.2f}",
                        f"{sum(prices)/len(prices):.2f}",
                        len(flights),
                        len(prices)
                    ])

        logger.info(f"Saved to {csv_file}")

        return json_file, csv_file


def main():
    """Demo run"""

    # URLs from user
    urls = [
        "https://fly.airalgerie.dz/plnext/AirAlgerie/Override.action;jsessionid=aF4Ee6AwH-TREPEsZFKpT98VstdYTRo2ItzQqGH1!1763137544642?BOOKING_FLOW=REVENUE&COUNTRY_SITE=GB&EMBEDDED_TRANSACTION=FlexPricerAvailability&ENC=35f680e7f1f36177444bf365b6c9b5bb6944e2e9bdc6e275e7d7123df98374681a62872eca90b2ef1f2c84e7c86424cae5d88fca610a135fb85e9e44b85196445af39e52dd84f550e02c325ac595bf792d0398eed172de62deae186304c006b038e4003131fa60a0de9b5f7f10192bc9f733ab52915e1afca2ad48e53963f0cbb4bad3163557ceea613b82794ed11a7e9d8c480377645e8194cd3d64528f347ee635a965ae5039b0c78224c59929ae872863136c86e300c2efe04a37a49387253fdaf27dd9f41d0c093fe3d5ed81d9bd624ada13b0733e0ba856ca97cc23bf01f8333cf7a801ed628336862754d7522eff6c9696eb012cae21de1bbc66d3280ee016b79b17f596e3280d1c4c7b5efacb3a67540efcd85d8d28c0ddad34788e5904c31daa220f4697da6545c1f95f44180faa517eb9aadc19ce927a250528494724269159a7b79ea08b6d6d5fb76eb88442a4eec6d436b899476e846c115d0713c1f4c6fe9b1feda1b62608b6ef629982217d781940c28680f69f20f0736eb625637621e11c8a2d2fe33bb6ec53dc7a87db3221b3a1ed82bb9b23beebda771e76f734eed50b785326ac8c000b5983ff42daefa7c9fb40f0a3067f808883c9560f3bd61322a1556bb2184db63c23f6156dcc5be33bd08e27820d33797b1d8a21379813becfc1ba7834bae2e7ffbbf897f6b781d41d0adfda537237a577e467c255800e852075ec02fd43de75e6a59dde99af749a102eae5a357bdda8b64c926e405dc652dce4dce59f87ec53e54f9bd5e743f7beb3c8d2f5b0066002849651d6c9718c39df8baea2b19ecde18c19da99e71952777e74bb09bb08ee42754388b529ff2bc13496feb934614d6db72d62ab91c5f90fcb3f511dc8810efd9aae1903c6bd86da80d4ea6064ea9d22dde0b11b2b562d17970fdfbbc09c5b79a3a2c68796e30e0cc274c12f4c7ae21146d83febfb4ebd543a61180f58f44165ee7c2ffe758541958166380a8b6a14fde3f2db4f56218e395f0c860a3dfbb55fb9dcc8316598aa1fdd41097fad25470daf85c8fec50f4afcbb01cdbdb77d54bd1969b9a2e219870bcc46745a5361114d93afed3c58d9521763c616d26fbc6471aa2318cf35277aae567ff8a1da5edb4373ede50ea4ab4bc6bd16dd6edc4f3357c73d89a4fd24c644d264166a505d316cc07f3c41304c7a9498def0157b6843b3d904f5b1cc32b9e763ea23f1e7f1fc04e364a662e5a6ab0471495bb7180cd1114e5093a32ad69413a1697c722cb3fe52b109b0596964d978db8edbf468b8b88498357d9389e104a8b7e943eeeffb35dfb2fff3a7e7a73ec46ff2cb5b98480ae8e8603ca6ce&ENCT=1&EXTERNAL_ID=BOOKING&LANGUAGE=GB&OFFICE_ID=ALGAH08AA&PAGE_ID=FPOW&SITE=P02IP02I&TRIP_FLOW=YES&_t=1763137548&force_device=",

        "https://fly.airalgerie.dz/plnext/AirAlgerie/Override.action;jsessionid=QiytaWrc2W26vJtNAkc88-RuSmJmY0cnjR5C5nLA!1763138685052?BOOKING_FLOW=REVENUE&COUNTRY_SITE=GB&EMBEDDED_TRANSACTION=FlexPricerAvailability&ENC=35f680e7f1f36177444bf365b6c9b5bb6944e2e9bdc6e275e7d7123df98374681a62872eca90b2ef1f2c84e7c86424cae5d88fca610a135fb85e9e44b85196445af39e52dd84f550e02c325ac595bf79abde63784969dcc307c15be13d09c684cd8fdea7c4ae258652f86c2dcdb7b01ef733ab52915e1afca2ad48e53963f0cb0d531b425ab4a63af7300ce0426728d1afde2a63a3f32db143fe1dc56e79964fe635a965ae5039b0c78224c59929ae872863136c86e300c2efe04a37a49387253fdaf27dd9f41d0c093fe3d5ed81d9bd624ada13b0733e0ba856ca97cc23bf019da466759872e43132e4e903404e8fc4ff6c9696eb012cae21de1bbc66d3280ead5a4105cbf7ce497e00711930518abb2b724222181ea0968ee7b86f4408c7dc04c31daa220f4697da6545c1f95f44180faa517eb9aadc19ce927a250528494724269159a7b79ea08b6d6d5fb76eb88442a4eec6d436b899476e846c115d0713c1f4c6fe9b1feda1b62608b6ef629982217d781940c28680f69f20f0736eb625637621e11c8a2d2fe33bb6ec53dc7a87db3221b3a1ed82bb9b23beebda771e76f734eed50b785326ac8c000b5983ff42daefa7c9fb40f0a3067f808883c9560f3bd61322a1556bb2184db63c23f6156dcc5be33bd08e27820d33797b1d8a21379813becfc1ba7834bae2e7ffbbf897f6b781d41d0adfda537237a577e467c255c4f756fa40a281109f0a7a8ad7476664ae6abeea6f39c375c761f42eeebebc3920212f78c92d18795ae7f03022b378102493144029cfb3d71b2f9705993c4397c0a5c7f4bbe533eba6ad95d096350fc719870bcc46745a5361114d93afed3c58adf4fce58a1e4731025e6babdec27f25277aae567ff8a1da5edb4373ede50ea437dbcd6cf288abb85e672652e6f2f3c149afef436efbea3ff6daae0bfee72fc77e76f0caf8f12f50cd990d08da5e44f2c99867f67b188c50cd3ff8fbf535cd015889bcda775ca5362080c1b9ca339f78e8f91712f89fbd6651e409dbc2fb66e68728c4f6e9da4bc12a2bed4fa732f6e5209c9d2eafbadbb1fd424b933fcd0a9eb92bb045df312609c581585de8108f74c9d9a3c9999299206c1ca6d7cf5de723955ca484460abece87abc39466a300a3ed9c9a8ba3bd400d9f5ef40b87459989934f506a1e3556c5a11c68dc6df026e1de022f4d81c8a54d8d37be06efb26b55b5a5db1b8bc94b5c20667267135fb675170ffaa0cb243b07c840e853c0196d4ef185e74fe0919253e85d13436a4785b922c3498a74edb4b50d5e3ca43c4e69e95409d50cd815685f3d43b0b85e8965dbfcf4c315c8f1cceae81a5cc0e91f03f0&ENCT=1&EXTERNAL_ID=BOOKING&LANGUAGE=FR&OFFICE_ID=ALGAH08AA&PAGE_ID=FPOW&SITE=P02IP02I&TRIP_FLOW=YES&_t=1763138687&force_device="
    ]

    parser = SimpleFlightParser()

    print("="*80)
    print(" "*20 + "Air Algerie Price Scraper Demo")
    print("="*80)
    print()

    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] Fetching URL...")
        result = parser.fetch_and_parse(url)

        if 'error' not in result:
            route = result.get('route', {})
            prices = result.get('all_prices', [])
            flights = result.get('flights', [])

            print(f"  Route: {route.get('origin', 'N/A')} → {route.get('destination', 'N/A')}")
            print(f"  Date: {route.get('date', 'N/A')}")
            print(f"  Prices found: {len(prices)}")
            if prices:
                print(f"  Price range: €{min(prices):.2f} - €{max(prices):.2f}")
            print(f"  Flights detected: {len(flights)}")
        else:
            print(f"  Error: {result['error']}")

    print("\n" + "="*80)
    print("Saving results...")
    json_file, csv_file = parser.save_results('demo')

    print("\n" + "="*80)
    print("RESULTS:")
    print("="*80)
    print(f"✓ JSON: {json_file}")
    print(f"✓ CSV:  {csv_file}")
    print(f"✓ Total URLs processed: {len(urls)}")
    print("="*80)


if __name__ == "__main__":
    main()
