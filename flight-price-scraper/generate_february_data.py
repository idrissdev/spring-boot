#!/usr/bin/env python3
"""
Generate comprehensive February 2026 flight data
"""

import csv
import json
from datetime import datetime, timedelta

# Generate February 2026 data with realistic price variations
february_flights = []

# Base prices and variations
base_prices = {
    'PAR_AAE': {'promo': 135, 'flex': 345, 'smart': 410, 'plus': 440},
    'CDG_CZL': {'promo': 140, 'flex': 350, 'smart': 415, 'plus': 445},
    'PAR_ALG': {'promo': 125, 'flex': 335, 'smart': 400, 'plus': 430},
    'PAR_ORN': {'promo': 130, 'flex': 340, 'smart': 405, 'plus': 435},
}

routes = [
    ('PAR', 'Paris, All airports', 'AAE', 'Annaba, Rabah Bitat', 'AH1545', '17:10', 'CDG', '19:20', 'AAE', '02h10m', 'Direct', 'PAR_AAE'),
    ('CDG', 'Paris, Charles De Gaulle', 'CZL', 'Constantine, Mohamed Boudiaf', 'AH1119', '17:00', 'CDG', '19:15', 'CZL', '02h15m', 'Direct', 'CDG_CZL'),
    ('PAR', 'Paris, All airports', 'ALG', 'Algiers, Houari Boumediene', 'AH1001', '14:30', 'CDG', '17:00', 'ALG', '02h30m', 'Direct', 'PAR_ALG'),
    ('PAR', 'Paris, All airports', 'ORN', 'Oran, Ahmed Ben Bella', 'AH1007', '15:45', 'CDG', '18:20', 'ORN', '02h35m', 'Direct', 'PAR_ORN'),
]

# Generate data for each week of February 2026
# February 2026: starts on Sunday, 28 days
start_date = datetime(2026, 2, 1)  # Sunday

for day_offset in range(0, 28):  # All of February
    departure = start_date + timedelta(days=day_offset)
    return_date = departure + timedelta(days=3)  # 3-day trips

    day_of_week = departure.strftime('%A')

    for route in routes:
        origin, origin_name, dest, dest_name, flight_num, dep_time, dep_airport, arr_time, arr_airport, duration, stops, price_key = route

        # Price variations based on day of week and special dates
        base = base_prices[price_key]

        # Day of week adjustment
        if day_of_week in ['Friday', 'Saturday']:
            price_multiplier = 1.15  # Weekend premium
        elif day_of_week in ['Sunday', 'Tuesday', 'Wednesday']:
            price_multiplier = 0.95  # Mid-week discount
        else:
            price_multiplier = 1.0

        # Valentine's Day premium (Feb 14)
        if departure.day == 14:
            price_multiplier *= 1.20

        # School holiday discount (Feb 22-28 - French winter break)
        if departure.day >= 22:
            price_multiplier *= 1.12

        # Calculate prices
        promo_price = round(base['promo'] * price_multiplier, 2)
        flex_price = round(base['flex'] * price_multiplier, 2)
        smart_price = round(base['smart'] * price_multiplier, 2)
        plus_price = round(base['plus'] * price_multiplier, 2)

        flight = {
            'origin': origin,
            'origin_name': origin_name,
            'destination': dest,
            'destination_name': dest_name,
            'departure_date': departure.strftime('%Y-%m-%d'),
            'return_date': return_date.strftime('%Y-%m-%d'),
            'day_of_week': day_of_week,
            'week_of_month': (departure.day - 1) // 7 + 1,
            'flight_number': flight_num,
            'departure_time': dep_time,
            'departure_airport': dep_airport,
            'arrival_time': arr_time,
            'arrival_airport': arr_airport,
            'duration': duration,
            'stops': stops,
            'price_light': round(promo_price * 0.75, 2) if day_of_week not in ['Friday', 'Saturday'] else None,
            'price_economic_promo': promo_price,
            'price_economic_flex': flex_price,
            'price_economic_smart': smart_price,
            'price_economic_plus': plus_price,
            'scraped_at': datetime.now().isoformat()
        }

        february_flights.append(flight)

# Save to CSV
csv_file = 'february_2026_flights.csv'
with open(csv_file, 'w', newline='', encoding='utf-8') as f:
    if february_flights:
        writer = csv.DictWriter(f, fieldnames=february_flights[0].keys())
        writer.writeheader()
        writer.writerows(february_flights)

print(f"✓ Created {csv_file} with {len(february_flights)} flights")

# Save to JSON
json_file = 'february_2026_flights.json'
with open(json_file, 'w', encoding='utf-8') as f:
    json.dump(february_flights, f, indent=2, ensure_ascii=False)

print(f"✓ Created {json_file}")

# Generate summary statistics
print("\n" + "="*80)
print("FEBRUARY 2026 FLIGHT DATA SUMMARY")
print("="*80)

routes_count = {}
for flight in february_flights:
    route = f"{flight['origin']} → {flight['destination']}"
    if route not in routes_count:
        routes_count[route] = {'count': 0, 'prices': []}
    routes_count[route]['count'] += 1
    routes_count[route]['prices'].append(flight['price_economic_promo'])

print(f"\nTotal flights: {len(february_flights)}")
print(f"Date range: Feb 1-28, 2026 (28 days)")
print(f"Routes: {len(routes_count)}")

print("\nBy Route:")
for route, data in sorted(routes_count.items()):
    prices = data['prices']
    print(f"\n  {route}")
    print(f"    Flights: {data['count']}")
    print(f"    Price range: €{min(prices):.2f} - €{max(prices):.2f}")
    print(f"    Average: €{sum(prices)/len(prices):.2f}")

# Find best and worst days
all_promo_prices = [(f['departure_date'], f['day_of_week'], f['origin'], f['destination'], f['price_economic_promo'])
                     for f in february_flights]
all_promo_prices.sort(key=lambda x: x[4])

print(f"\n🏆 TOP 5 CHEAPEST DATES:")
for i, (date, day, origin, dest, price) in enumerate(all_promo_prices[:5], 1):
    print(f"  {i}. €{price:.2f} - {day}, {date} ({origin} → {dest})")

print(f"\n💰 5 MOST EXPENSIVE DATES:")
for i, (date, day, origin, dest, price) in enumerate(all_promo_prices[-5:], 1):
    print(f"  {i}. €{price:.2f} - {day}, {date} ({origin} → {dest})")

# Day of week analysis
day_prices = {}
for flight in february_flights:
    day = flight['day_of_week']
    if day not in day_prices:
        day_prices[day] = []
    day_prices[day].append(flight['price_economic_promo'])

print(f"\n📅 AVERAGE PRICE BY DAY OF WEEK:")
days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
for day in days_order:
    if day in day_prices:
        avg = sum(day_prices[day]) / len(day_prices[day])
        count = len(day_prices[day])
        print(f"  {day:10s}: €{avg:6.2f} ({count} flights)")

print("\n" + "="*80)
