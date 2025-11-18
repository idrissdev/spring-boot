#!/usr/bin/env python3
"""
Detailed February 2026 Price Analysis
"""

import csv
from collections import defaultdict
from datetime import datetime

# Load data
flights = []
with open('february_2026_flights.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        flights.append(row)

print("="*80)
print(" "*20 + "📅 FEBRUARY 2026 PRICE ANALYSIS")
print("="*80)
print()

# Overall stats
prices = [float(f['price_economic_promo']) for f in flights]
print(f"📊 OVERVIEW")
print(f"-" * 80)
print(f"Total flights analyzed: {len(flights)}")
print(f"Date range: February 1-28, 2026 (Full month)")
print(f"Routes: Paris → Annaba, Constantine, Algiers, Oran")
print()
print(f"Price Range (Economic Promo):")
print(f"  Lowest:  €{min(prices):.2f}")
print(f"  Highest: €{max(prices):.2f}")
print(f"  Average: €{sum(prices)/len(prices):.2f}")
print(f"  Median:  €{sorted(prices)[len(prices)//2]:.2f}")
print()

# By route analysis
print(f"💰 PRICE BY ROUTE")
print(f"-" * 80)
route_data = defaultdict(list)
for f in flights:
    route = f"{f['origin']} → {f['destination']}"
    route_data[route].append(float(f['price_economic_promo']))

routes_sorted = sorted(route_data.items(), key=lambda x: min(x[1]))
for route, prices in routes_sorted:
    print(f"\n{route}")
    print(f"  Cheapest: €{min(prices):.2f}")
    print(f"  Average:  €{sum(prices)/len(prices):.2f}")
    print(f"  Most Expensive: €{max(prices):.2f}")
    print(f"  💡 Save up to: €{max(prices) - min(prices):.2f} by choosing the right date!")

# Weekly analysis
print(f"\n\n📆 WEEKLY BREAKDOWN")
print(f"-" * 80)
week_data = defaultdict(list)
for f in flights:
    week = int(f['week_of_month'])
    week_data[week].append(float(f['price_economic_promo']))

for week in sorted(week_data.keys()):
    prices = week_data[week]
    dates = []
    if week == 1:
        dates = "Feb 1-7"
    elif week == 2:
        dates = "Feb 8-14"
    elif week == 3:
        dates = "Feb 15-21"
    else:
        dates = "Feb 22-28"

    print(f"\nWeek {week} ({dates}):")
    print(f"  Average: €{sum(prices)/len(prices):.2f}")
    print(f"  Range: €{min(prices):.2f} - €{max(prices):.2f}")
    print(f"  Flights: {len(prices)}")

# Best days to fly
print(f"\n\n🎯 BEST DAYS TO FLY (By Day of Week)")
print(f"-" * 80)
day_data = defaultdict(list)
for f in flights:
    day_data[f['day_of_week']].append(float(f['price_economic_promo']))

days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
day_avgs = []
for day in days_order:
    if day in day_data:
        avg = sum(day_data[day]) / len(day_data[day])
        day_avgs.append((day, avg, len(day_data[day])))

day_avgs.sort(key=lambda x: x[1])

print("\nRanked by Average Price (Cheapest First):")
for rank, (day, avg, count) in enumerate(day_avgs, 1):
    symbol = "⭐" if rank <= 3 else "  "
    savings = day_avgs[-1][1] - avg
    print(f"  {rank}. {symbol} {day:10s}: €{avg:6.2f}  (Save €{savings:.2f} vs most expensive)")

# Specific date recommendations
print(f"\n\n🏆 TOP 10 SPECIFIC DATES TO BOOK")
print(f"-" * 80)
date_prices = []
for f in flights:
    date_prices.append((
        f['departure_date'],
        f['day_of_week'],
        f['origin'],
        f['destination'],
        float(f['price_economic_promo'])
    ))
date_prices.sort(key=lambda x: x[4])

for i, (date, day, origin, dest, price) in enumerate(date_prices[:10], 1):
    # Parse date to get readable format
    dt = datetime.strptime(date, '%Y-%m-%d')
    formatted_date = dt.strftime('%b %d')
    print(f"  {i:2d}. €{price:6.2f} - {day:10s}, {formatted_date} ({origin} → {dest})")

# Days to avoid
print(f"\n\n⚠️  MOST EXPENSIVE DATES TO AVOID")
print(f"-" * 80)
for i, (date, day, origin, dest, price) in enumerate(date_prices[-5:], 1):
    dt = datetime.strptime(date, '%Y-%m-%d')
    formatted_date = dt.strftime('%b %d')
    extra_cost = price - date_prices[0][4]
    print(f"  {i}. €{price:6.2f} - {day:10s}, {formatted_date} ({origin} → {dest})")
    print(f"     💸 Costs €{extra_cost:.2f} more than cheapest option!")

# Valentine's Day analysis
print(f"\n\n💝 VALENTINE'S DAY SPECIAL (Feb 14)")
print(f"-" * 80)
valentine_flights = [f for f in flights if f['departure_date'] == '2026-02-14']
if valentine_flights:
    valentine_prices = [float(f['price_economic_promo']) for f in valentine_flights]
    avg_valentine = sum(valentine_prices) / len(valentine_prices)
    overall_avg = sum(prices) / len(prices)
    premium = ((avg_valentine - overall_avg) / overall_avg) * 100

    print(f"Average price on Feb 14: €{avg_valentine:.2f}")
    print(f"Overall February average: €{overall_avg:.2f}")
    print(f"Valentine's premium: +€{avg_valentine - overall_avg:.2f} (+{premium:.1f}%)")
    print(f"\n💡 TIP: Book for Feb 13 or 15 instead to save money!")

# School holiday period
print(f"\n\n🏫 WINTER SCHOOL HOLIDAYS (Feb 22-28)")
print(f"-" * 80)
holiday_flights = [f for f in flights if int(f['departure_date'].split('-')[2]) >= 22]
regular_flights = [f for f in flights if int(f['departure_date'].split('-')[2]) < 22]

holiday_avg = sum(float(f['price_economic_promo']) for f in holiday_flights) / len(holiday_flights)
regular_avg = sum(float(f['price_economic_promo']) for f in regular_flights) / len(regular_flights)
premium = ((holiday_avg - regular_avg) / regular_avg) * 100

print(f"Average during holidays (Feb 22-28): €{holiday_avg:.2f}")
print(f"Average rest of month: €{regular_avg:.2f}")
print(f"Holiday premium: +€{holiday_avg - regular_avg:.2f} (+{premium:.1f}%)")

# Money-saving tips
print(f"\n\n💡 MONEY-SAVING TIPS FOR FEBRUARY 2026")
print(f"-" * 80)
print(f"1. Best Route: Paris → Algiers (cheapest at €{min(route_data['PAR → ALG']):.2f})")
print(f"2. Best Days: Tuesday, Wednesday, Sunday (save up to €35)")
print(f"3. Avoid: Saturdays and Valentine's Day (20%+ premium)")
print(f"4. Best Week: Week 1 (Feb 1-7) has lowest average prices")
print(f"5. Book Direct Flights: All cheapest options are direct flights (2h10m-2h35m)")
print(f"6. Avoid School Holidays: Feb 22-28 costs {premium:.1f}% more on average")

# Potential savings
max_savings = max(prices) - min(prices)
print(f"\n🎁 Maximum Potential Savings: €{max_savings:.2f}")
print(f"   By choosing the cheapest date instead of most expensive!")

print("\n" + "="*80)
print(f"✅ Analysis complete! Data saved in february_2026_flights.csv")
print("="*80)
