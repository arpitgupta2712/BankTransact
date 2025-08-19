#!/usr/bin/env python3
"""
Create a simple party summary list from the party analysis results
"""

import pandas as pd
import os
import glob
from datetime import datetime

def create_party_list():
    """Create a simple party list with totals"""
    
    # Use the clean filename
    party_file = "data/income/party/axis_income_with_parties.csv"
    
    if not os.path.exists(party_file):
        print("❌ No party analysis files found. Please run party_analysis.py first.")
        return None, None
    
    print(f"📊 Using party analysis file: {party_file}")
    
    # Read the enhanced CSV with party names
    df = pd.read_csv(party_file)
    
    # Filter out uncategorized transactions
    categorized_df = df[df['party_name'] != 'Uncategorized']
    
    # Group by party and sum amounts
    party_summary = categorized_df.groupby('party_name').agg({
        'amount': ['sum', 'count']
    }).round(2)
    
    # Flatten column names
    party_summary.columns = ['total_amount', 'transaction_count']
    party_summary = party_summary.reset_index()
    
    # Sort by total amount (descending)
    party_summary = party_summary.sort_values('total_amount', ascending=False)
    
    # Calculate percentage of total
    total_categorized = party_summary['total_amount'].sum()
    party_summary['percentage'] = (party_summary['total_amount'] / total_categorized * 100).round(1)
    
    # Create output file with clean naming
    output_file = "data/summary/party_list_summary.txt"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("AXIS BANK - PARTY LIST SUMMARY\n")
        f.write("=" * 80 + "\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total categorized amount: ₹{total_categorized:,.2f}\n")
        f.write(f"Total parties: {len(party_summary)}\n\n")
        
        f.write("🏢 PARTY WISE INCOME SUMMARY\n")
        f.write("-" * 80 + "\n")
        f.write(f"{'Rank':<4} {'Party Name':<40} {'Amount (₹)':<15} {'Count':<8} {'%':<6}\n")
        f.write("-" * 80 + "\n")
        
        for i, row in party_summary.iterrows():
            rank = i + 1
            party_name = row['party_name'][:39]  # Truncate if too long
            amount = f"{row['total_amount']:,.2f}"
            count = int(row['transaction_count'])
            percentage = f"{row['percentage']:.1f}%"
            
            f.write(f"{rank:<4} {party_name:<40} {amount:<15} {count:<8} {percentage:<6}\n")
        
        f.write("-" * 80 + "\n")
        f.write(f"{'TOTAL':<44} {total_categorized:>15,.2f} {'100.0%':>14}\n")
        f.write("=" * 80 + "\n")
    
    print(f"📄 Party list summary saved to: {output_file}")
    
    # Also create a CSV version
    csv_file = "data/income/party/party_list_summary.csv"
    party_summary.to_csv(csv_file, index=False)
    print(f"📊 Party list CSV saved to: {csv_file}")
    
    return output_file, csv_file

if __name__ == "__main__":
    create_party_list()
