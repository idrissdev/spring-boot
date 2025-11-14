#!/usr/bin/env python3
"""
Price Analysis Tool
Analyze scraped flight prices to find best deals
"""

import pandas as pd
import json
import sys
from datetime import datetime
from pathlib import Path


class FlightPriceAnalyzer:
    """Analyze flight price data"""

    def __init__(self, csv_file: str = None, json_file: str = None):
        self.df = None
        self.data = None

        if csv_file and Path(csv_file).exists():
            self.load_csv(csv_file)

        if json_file and Path(json_file).exists():
            self.load_json(json_file)

    def load_csv(self, filename: str):
        """Load data from CSV"""
        try:
            self.df = pd.read_csv(filename)
            print(f"✓ Loaded {len(self.df)} records from {filename}")
        except Exception as e:
            print(f"✗ Error loading CSV: {e}")

    def load_json(self, filename: str):
        """Load data from JSON"""
        try:
            with open(filename, 'r') as f:
                self.data = json.load(f)
            print(f"✓ Loaded {len(self.data)} results from {filename}")
        except Exception as e:
            print(f"✗ Error loading JSON: {e}")

    def find_cheapest_flights(self, fare_class: str = 'price_economic_promo', top_n: int = 10):
        """Find the cheapest flights"""
        if self.df is None:
            print("No CSV data loaded")
            return

        print(f"\n{'='*80}")
        print(f"Top {top_n} Cheapest Flights - {fare_class.replace('price_', '').replace('_', ' ').title()}")
        print(f"{'='*80}\n")

        # Filter out null prices
        valid_df = self.df[self.df[fare_class].notna()].copy()

        if valid_df.empty:
            print(f"No prices found for {fare_class}")
            return

        # Sort by price
        cheapest = valid_df.nsmallest(top_n, fare_class)

        # Display results
        for idx, row in cheapest.iterrows():
            print(f"{row.get('origin', 'N/A')} → {row.get('destination', 'N/A')}")
            print(f"  Date: {row.get('departure_date', 'N/A')}")
            print(f"  Flight: {row.get('flight_number', 'N/A')}")
            print(f"  Time: {row.get('departure_time', 'N/A')} - {row.get('arrival_time', 'N/A')}")
            print(f"  Price: €{row[fare_class]:.2f}")
            print()

    def compare_routes(self):
        """Compare average prices across routes"""
        if self.df is None:
            print("No CSV data loaded")
            return

        print(f"\n{'='*80}")
        print("Average Prices by Route")
        print(f"{'='*80}\n")

        # Group by route
        if 'origin' in self.df.columns and 'destination' in self.df.columns:
            self.df['route'] = self.df['origin'] + ' → ' + self.df['destination']

            # Calculate average for each price column
            price_cols = [col for col in self.df.columns if col.startswith('price_')]

            if price_cols:
                route_stats = self.df.groupby('route')[price_cols].agg(['mean', 'min', 'max'])

                print(route_stats.to_string())
            else:
                print("No price columns found")

    def find_best_dates(self, route_origin: str = None, route_dest: str = None,
                       fare_class: str = 'price_economic_promo'):
        """Find best dates to fly for a specific route"""
        if self.df is None:
            print("No CSV data loaded")
            return

        print(f"\n{'='*80}")
        print(f"Best Dates to Fly - {fare_class.replace('price_', '').replace('_', ' ').title()}")
        print(f"{'='*80}\n")

        # Filter by route if specified
        df = self.df.copy()

        if route_origin:
            df = df[df['origin'] == route_origin]

        if route_dest:
            df = df[df['destination'] == route_dest]

        # Filter valid prices
        df = df[df[fare_class].notna()]

        if df.empty:
            print("No data found for the specified route")
            return

        # Group by departure date
        if 'departure_date' in df.columns:
            date_prices = df.groupby('departure_date')[fare_class].agg(['min', 'mean', 'count'])
            date_prices = date_prices.sort_values('min')

            print(f"{'Date':<15} {'Min Price':>12} {'Avg Price':>12} {'Flights':>10}")
            print("-" * 55)

            for date, row in date_prices.head(20).iterrows():
                print(f"{date:<15} €{row['min']:>10.2f} €{row['mean']:>10.2f} {int(row['count']):>10}")

    def price_distribution(self, fare_class: str = 'price_economic_promo'):
        """Show price distribution"""
        if self.df is None:
            print("No CSV data loaded")
            return

        print(f"\n{'='*80}")
        print(f"Price Distribution - {fare_class.replace('price_', '').replace('_', ' ').title()}")
        print(f"{'='*80}\n")

        prices = self.df[fare_class].dropna()

        if prices.empty:
            print(f"No prices found for {fare_class}")
            return

        stats = prices.describe()

        print(f"Total flights: {len(prices)}")
        print(f"Min price:     €{stats['min']:.2f}")
        print(f"Max price:     €{stats['max']:.2f}")
        print(f"Mean price:    €{stats['mean']:.2f}")
        print(f"Median price:  €{stats['50%']:.2f}")
        print(f"Std deviation: €{stats['std']:.2f}")

        print("\nPercentiles:")
        print(f"  25%: €{stats['25%']:.2f}")
        print(f"  50%: €{stats['50%']:.2f}")
        print(f"  75%: €{stats['75%']:.2f}")

    def fare_class_comparison(self):
        """Compare all fare classes"""
        if self.df is None:
            print("No CSV data loaded")
            return

        print(f"\n{'='*80}")
        print("Fare Class Comparison")
        print(f"{'='*80}\n")

        price_cols = [col for col in self.df.columns if col.startswith('price_')]

        if not price_cols:
            print("No price columns found")
            return

        print(f"{'Fare Class':<25} {'Min':>10} {'Avg':>10} {'Max':>10} {'Count':>10}")
        print("-" * 70)

        for col in price_cols:
            prices = self.df[col].dropna()

            if not prices.empty:
                fare_name = col.replace('price_', '').replace('_', ' ').title()
                print(f"{fare_name:<25} €{prices.min():>8.2f} €{prices.mean():>8.2f} €{prices.max():>8.2f} {len(prices):>10}")

    def export_best_deals(self, output_file: str = 'best_deals.csv', max_price: float = 150.0):
        """Export flights below a certain price"""
        if self.df is None:
            print("No CSV data loaded")
            return

        price_cols = [col for col in self.df.columns if col.startswith('price_')]

        if not price_cols:
            print("No price columns found")
            return

        # Find rows where any price is below threshold
        mask = False
        for col in price_cols:
            mask = mask | (self.df[col] <= max_price)

        deals = self.df[mask]

        if not deals.empty:
            deals.to_csv(output_file, index=False)
            print(f"\n✓ Exported {len(deals)} deals under €{max_price:.2f} to {output_file}")
        else:
            print(f"\n✗ No deals found under €{max_price:.2f}")

    def generate_report(self):
        """Generate comprehensive analysis report"""
        if self.df is None:
            print("No CSV data loaded")
            return

        print("\n" + "="*80)
        print(" "*25 + "FLIGHT PRICE ANALYSIS REPORT")
        print("="*80)

        print(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total records: {len(self.df)}")

        # Price distribution for main fare class
        self.price_distribution('price_economic_promo')

        # Compare all fare classes
        self.fare_class_comparison()

        # Compare routes
        self.compare_routes()

        # Find cheapest
        self.find_cheapest_flights(top_n=10)

        print("\n" + "="*80)
        print("End of Report")
        print("="*80 + "\n")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Analyze Air Algerie flight prices')

    parser.add_argument(
        '--csv',
        default='airalgerie_prices_q1_2026.csv',
        help='CSV file to analyze'
    )

    parser.add_argument(
        '--json',
        default='airalgerie_prices_q1_2026.json',
        help='JSON file to analyze'
    )

    parser.add_argument(
        '--report',
        action='store_true',
        help='Generate full analysis report'
    )

    parser.add_argument(
        '--cheapest',
        type=int,
        metavar='N',
        help='Show N cheapest flights'
    )

    parser.add_argument(
        '--fare-class',
        default='price_economic_promo',
        choices=['price_light', 'price_economic_promo', 'price_economic_flex',
                'price_economic_smart', 'price_economic_plus'],
        help='Fare class to analyze'
    )

    parser.add_argument(
        '--best-dates',
        nargs=2,
        metavar=('ORIGIN', 'DEST'),
        help='Find best dates for a route (e.g., PAR AAE)'
    )

    parser.add_argument(
        '--export-deals',
        type=float,
        metavar='MAX_PRICE',
        help='Export deals below this price (e.g., 150.0)'
    )

    args = parser.parse_args()

    # Create analyzer
    analyzer = FlightPriceAnalyzer(csv_file=args.csv, json_file=args.json)

    if analyzer.df is None:
        print("\nNo data loaded. Please check file paths.")
        print(f"Expected CSV: {args.csv}")
        print(f"Expected JSON: {args.json}")
        sys.exit(1)

    # Run requested analysis
    if args.report:
        analyzer.generate_report()
    elif args.cheapest:
        analyzer.find_cheapest_flights(fare_class=args.fare_class, top_n=args.cheapest)
    elif args.best_dates:
        analyzer.find_best_dates(
            route_origin=args.best_dates[0],
            route_dest=args.best_dates[1],
            fare_class=args.fare_class
        )
    elif args.export_deals:
        analyzer.export_best_deals(max_price=args.export_deals)
    else:
        # Default: show summary
        analyzer.generate_report()


if __name__ == "__main__":
    main()
