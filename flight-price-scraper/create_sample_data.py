#!/usr/bin/env python3
"""
Create sample flight data based on user's provided information
"""

import csv
import json
from datetime import datetime

# Sample data from user's examples
sample_flights = [
    # Paris -> Annaba (Dec 9-12)
    {
        'origin': 'PAR',
        'origin_name': 'Paris, All airports',
        'destination': 'AAE',
        'destination_name': 'Annaba, Rabah Bitat',
        'departure_date': '2025-12-09',
        'return_date': '2025-12-12',
        'flight_number': 'AH1545',
        'departure_time': '17:10',
        'departure_airport': 'CDG',
        'arrival_time': '19:20',
        'arrival_airport': 'AAE',
        'duration': '02h10m',
        'stops': 'Direct',
        'price_light': 99.60,
        'price_economic_promo': 134.60,
        'price_economic_flex': 329.60,
        'price_economic_smart': 406.60,
        'price_economic_plus': 434.60,
        'scraped_at': datetime.now().isoformat()
    },
    {
        'origin': 'PAR',
        'origin_name': 'Paris, All airports',
        'destination': 'AAE',
        'destination_name': 'Annaba, Rabah Bitat',
        'departure_date': '2025-12-09',
        'return_date': '2025-12-12',
        'flight_number': 'AH1001 + AH6006',
        'departure_time': '14:30',
        'departure_airport': 'CDG',
        'arrival_time': '21:10',
        'arrival_airport': 'AAE',
        'duration': '06h40m',
        'stops': '1 stop',
        'price_light': None,
        'price_economic_promo': 161.61,
        'price_economic_flex': 351.61,
        'price_economic_smart': 433.61,
        'price_economic_plus': None,
        'scraped_at': datetime.now().isoformat()
    },
    {
        'origin': 'PAR',
        'origin_name': 'Paris, All airports',
        'destination': 'AAE',
        'destination_name': 'Annaba, Rabah Bitat',
        'departure_date': '2025-12-09',
        'return_date': '2025-12-12',
        'flight_number': 'AH1011 + AH6006',
        'departure_time': '13:00',
        'departure_airport': 'ORY',
        'arrival_time': '21:10',
        'arrival_airport': 'AAE',
        'duration': '08h10m',
        'stops': '1 stop',
        'price_light': None,
        'price_economic_promo': 158.60,
        'price_economic_flex': 348.60,
        'price_economic_smart': 430.60,
        'price_economic_plus': None,
        'scraped_at': datetime.now().isoformat()
    },

    # Paris -> Constantine (Jan 7-10, 2026)
    {
        'origin': 'CDG',
        'origin_name': 'Paris, Charles De Gaulle',
        'destination': 'CZL',
        'destination_name': 'Constantine, Mohamed Boudiaf',
        'departure_date': '2026-01-07',
        'return_date': '2026-01-10',
        'flight_number': 'AH1119',
        'departure_time': '17:00',
        'departure_airport': 'CDG',
        'arrival_time': '19:15',
        'arrival_airport': 'CZL',
        'duration': '02h15m',
        'stops': 'Direct',
        'price_light': None,
        'price_economic_promo': 134.60,
        'price_economic_flex': 348.60,
        'price_economic_smart': 415.60,
        'price_economic_plus': 444.60,
        'scraped_at': datetime.now().isoformat()
    },
    {
        'origin': 'CDG',
        'origin_name': 'Paris, Charles De Gaulle',
        'destination': 'CZL',
        'destination_name': 'Constantine, Mohamed Boudiaf',
        'departure_date': '2026-01-07',
        'return_date': '2026-01-10',
        'flight_number': 'AH1003 + AH6196',
        'departure_time': '11:15',
        'departure_airport': 'CDG',
        'arrival_time': '18:50',
        'arrival_airport': 'CZL',
        'duration': '07h35m',
        'stops': '1 stop',
        'price_light': None,
        'price_economic_promo': 155.61,
        'price_economic_flex': 345.61,
        'price_economic_smart': 427.61,
        'price_economic_plus': None,
        'scraped_at': datetime.now().isoformat()
    },

    # Additional calendar prices for different dates
    {
        'origin': 'PAR',
        'origin_name': 'Paris, All airports',
        'destination': 'AAE',
        'destination_name': 'Annaba, Rabah Bitat',
        'departure_date': '2025-12-07',
        'return_date': '2025-12-10',
        'flight_number': 'AH1545',
        'departure_time': '17:10',
        'departure_airport': 'CDG',
        'arrival_time': '19:20',
        'arrival_airport': 'AAE',
        'duration': '02h10m',
        'stops': 'Direct',
        'price_light': None,
        'price_economic_promo': 96.59,  # Sunday - cheaper!
        'price_economic_flex': 326.59,
        'price_economic_smart': 403.59,
        'price_economic_plus': 431.59,
        'scraped_at': datetime.now().isoformat()
    },
    {
        'origin': 'PAR',
        'origin_name': 'Paris, All airports',
        'destination': 'AAE',
        'destination_name': 'Annaba, Rabah Bitat',
        'departure_date': '2025-12-06',
        'return_date': '2025-12-09',
        'flight_number': 'AH1545',
        'departure_time': '17:10',
        'departure_airport': 'CDG',
        'arrival_time': '19:20',
        'arrival_airport': 'AAE',
        'duration': '02h10m',
        'stops': 'Direct',
        'price_light': None,
        'price_economic_promo': 158.60,  # Saturday - more expensive
        'price_economic_flex': 388.60,
        'price_economic_smart': 465.60,
        'price_economic_plus': 493.60,
        'scraped_at': datetime.now().isoformat()
    },

    # Q1 2026 samples
    {
        'origin': 'CDG',
        'origin_name': 'Paris, Charles De Gaulle',
        'destination': 'CZL',
        'destination_name': 'Constantine, Mohamed Boudiaf',
        'departure_date': '2026-01-08',
        'return_date': '2026-01-11',
        'flight_number': 'AH1119',
        'departure_time': '17:00',
        'departure_airport': 'CDG',
        'arrival_time': '19:15',
        'arrival_airport': 'CZL',
        'duration': '02h15m',
        'stops': 'Direct',
        'price_light': None,
        'price_economic_promo': 134.60,
        'price_economic_flex': 348.60,
        'price_economic_smart': 415.60,
        'price_economic_plus': 444.60,
        'scraped_at': datetime.now().isoformat()
    },
    {
        'origin': 'CDG',
        'origin_name': 'Paris, Charles De Gaulle',
        'destination': 'CZL',
        'destination_name': 'Constantine, Mohamed Boudiaf',
        'departure_date': '2026-02-14',
        'return_date': '2026-02-17',
        'flight_number': 'AH1119',
        'departure_time': '17:00',
        'departure_airport': 'CDG',
        'arrival_time': '19:15',
        'arrival_airport': 'CZL',
        'duration': '02h15m',
        'stops': 'Direct',
        'price_light': None,
        'price_economic_promo': 145.60,  # Valentine's - slightly higher
        'price_economic_flex': 358.60,
        'price_economic_smart': 425.60,
        'price_economic_plus': 454.60,
        'scraped_at': datetime.now().isoformat()
    },
    {
        'origin': 'CDG',
        'origin_name': 'Paris, Charles De Gaulle',
        'destination': 'CZL',
        'destination_name': 'Constantine, Mohamed Boudiaf',
        'departure_date': '2026-03-20',
        'return_date': '2026-03-23',
        'flight_number': 'AH1119',
        'departure_time': '17:00',
        'departure_airport': 'CDG',
        'arrival_time': '19:15',
        'arrival_airport': 'CZL',
        'duration': '02h15m',
        'stops': 'Direct',
        'price_light': None,
        'price_economic_promo': 128.60,  # Mid-March - good deal!
        'price_economic_flex': 338.60,
        'price_economic_smart': 405.60,
        'price_economic_plus': 434.60,
        'scraped_at': datetime.now().isoformat()
    },
]

# Save to CSV
csv_file = 'sample_results.csv'
with open(csv_file, 'w', newline='', encoding='utf-8') as f:
    if sample_flights:
        writer = csv.DictWriter(f, fieldnames=sample_flights[0].keys())
        writer.writeheader()
        writer.writerows(sample_flights)

print(f"✓ Created {csv_file} with {len(sample_flights)} sample flights")

# Save to JSON
json_file = 'sample_results.json'
with open(json_file, 'w', encoding='utf-8') as f:
    json.dump(sample_flights, f, indent=2, ensure_ascii=False)

print(f"✓ Created {json_file}")

# Print summary
print("\n" + "="*80)
print("SAMPLE DATA SUMMARY")
print("="*80)

routes = {}
for flight in sample_flights:
    route_key = f"{flight['origin']} → {flight['destination']}"
    if route_key not in routes:
        routes[route_key] = {'count': 0, 'prices': []}
    routes[route_key]['count'] += 1
    if flight['price_economic_promo']:
        routes[route_key]['prices'].append(flight['price_economic_promo'])

print(f"\nTotal flights: {len(sample_flights)}")
print(f"Routes: {len(routes)}")
print("\nBy Route:")
for route, data in routes.items():
    if data['prices']:
        print(f"  {route}")
        print(f"    Flights: {data['count']}")
        print(f"    Price range: €{min(data['prices']):.2f} - €{max(data['prices']):.2f}")
        print(f"    Average: €{sum(data['prices'])/len(data['prices']):.2f}")

# Find cheapest
cheapest = min([f for f in sample_flights if f['price_economic_promo']],
               key=lambda x: x['price_economic_promo'])

print(f"\n🏆 CHEAPEST FLIGHT (Economic Promo):")
print(f"  {cheapest['origin']} → {cheapest['destination']}")
print(f"  Date: {cheapest['departure_date']}")
print(f"  Flight: {cheapest['flight_number']}")
print(f"  Price: €{cheapest['price_economic_promo']:.2f}")

print("\n" + "="*80)
