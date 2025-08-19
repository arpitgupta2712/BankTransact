#!/usr/bin/env python3
"""
Party Name Analysis and Categorization for AXIS Bank Income Transactions
Extracts party names from transaction narrations and generates party-wise summaries
"""

import pandas as pd
import re
import os
import glob
from collections import defaultdict
from datetime import datetime

class PartyAnalyzer:
    
    def __init__(self, income_file_path):
        self.income_file_path = income_file_path
        self.party_totals = defaultdict(float)
        self.party_transactions = defaultdict(list)
        self.uncategorized_transactions = []
        
    def extract_party_name(self, narration):
        """
        Intelligently extract party name from transaction narration
        Returns the party name or None if no valid party found
        """
        if pd.isna(narration) or narration == '':
            return None
            
        narration = str(narration).strip()
        
        # Pattern 1: NEFT transactions with party name
        # Format: NEFT/REFERENCE/PARTY_NAME/BANK_NAME/...
        neft_pattern = r'NEFT/[^/]+/([^/]+)/[^/]+'
        match = re.search(neft_pattern, narration)
        if match:
            party_name = match.group(1).strip()
            if self.is_valid_party_name(party_name):
                return self.clean_party_name(party_name)
        
        # Pattern 2: RTGS transactions
        # Format: RTGS/REFERENCE/PARTY_NAME/BANK_NAME/...
        rtgs_pattern = r'RTGS/[^/]+/([^/]+)/[^/]+'
        match = re.search(rtgs_pattern, narration)
        if match:
            party_name = match.group(1).strip()
            if self.is_valid_party_name(party_name):
                return self.clean_party_name(party_name)
        
        # Pattern 3: TRF (Transfer) transactions
        # Format: TRF/PARTY_NAME/transfer
        trf_pattern = r'TRF/([^/]+)/transfer'
        match = re.search(trf_pattern, narration)
        if match:
            party_name = match.group(1).strip()
            if self.is_valid_party_name(party_name):
                return self.clean_party_name(party_name)
        
        # Pattern 4: IFT (Internal Fund Transfer) with party name
        # Format: IFT/BRANCH/REFERENCE/PARTY_NAME/...
        ift_pattern = r'IFT/[^/]+/[^/]+/([^/]+)/'
        match = re.search(ift_pattern, narration)
        if match:
            party_name = match.group(1).strip()
            if self.is_valid_party_name(party_name):
                return self.clean_party_name(party_name)
        
        # Pattern 5: MOB/TPFT transactions
        # Format: MOB/TPFT/PARTY_NAME/REFERENCE
        mob_pattern = r'MOB/TPFT/([^/]+)/'
        match = re.search(mob_pattern, narration)
        if match:
            party_name = match.group(1).strip()
            if self.is_valid_party_name(party_name):
                return self.clean_party_name(party_name)
        
        # Pattern 6: IFT with different format (IFT/CB.../REFERENCE/PARTY_NAME/...)
        ift_pattern2 = r'IFT/[^/]+/[^/]+/([^/]+)/[^/]+'
        match = re.search(ift_pattern2, narration)
        if match:
            party_name = match.group(1).strip()
            if self.is_valid_party_name(party_name):
                return self.clean_party_name(party_name)
        
        # Pattern 7: NEFT with AXCT reference (BELZ INSTRUMENTS pattern)
        # Format: NEFT/AXCT.../PARTY_NAME/AXIS BANK/
        axct_pattern = r'NEFT/AXCT[^/]+/([^/]+)/AXIS BANK/'
        match = re.search(axct_pattern, narration)
        if match:
            party_name = match.group(1).strip()
            if self.is_valid_party_name(party_name):
                return self.clean_party_name(party_name)
        
        # Pattern 7b: NEFT with AXCT reference (BELZ INSTRUMENTS pattern) - more specific
        # Format: NEFT/AXCT.../BELZ INSTRUMENTS PVT.LTD/AXIS BANK/
        belz_pattern = r'NEFT/AXCT[^/]+/BELZ INSTRUMENTS PVT\.LTD/AXIS BANK/'
        if re.search(belz_pattern, narration):
            return "BELZ INSTRUMENTS PVT LTD"
        
        # Pattern 8: NEFT with HDFC Bank Ltd pattern
        # Format: NEFT/.../HDFC Bank Ltd/HDFC BANK/...
        hdfc_pattern = r'NEFT/[^/]+/HDFC Bank Ltd/HDFC BANK/'
        if re.search(hdfc_pattern, narration):
            return "HDFC Bank Ltd"
        
        # Pattern 9: NEFT with GRAVITI PHARMACEUTICALS pattern
        # Format: NEFT/.../GRAVITI PHARMACEUTICALS PVT/HDFC BANK/...
        graviti_pattern = r'NEFT/[^/]+/GRAVITI PHARMACEUTICALS PVT/HDFC BANK/'
        if re.search(graviti_pattern, narration):
            return "GRAVITI PHARMACEUTICALS PVT"
        
        # Pattern 10: NEFT with HERO MOTOCORP pattern
        # Format: NEFT/.../HERO MOTOCORP LIMITED/HDFC BANK/...
        hero_pattern = r'NEFT/[^/]+/HERO MOTOCORP LIMITED/HDFC BANK/'
        if re.search(hero_pattern, narration):
            return "HERO MOTOCORP LIMITED"
        
        # Pattern 11: NEFT with AXISCAL INSTRUMENTS pattern
        # Format: NEFT/.../AXISCAL INSTRUMENTS PRIVATE/BANK OF INDIA/...
        axiscal_pattern = r'NEFT/[^/]+/AXISCAL INSTRUMENTS PRIVATE/BANK OF INDIA/'
        if re.search(axiscal_pattern, narration):
            return "AXISCAL INSTRUMENTS PRIVATE"
        
        # Pattern 12: TRF with SIGMA TEST RESEARCH CENTRE
        # Format: TRF/SIGMA TEST RESEARCH CENTRE/TRANSFER
        sigma_pattern = r'TRF/SIGMA TEST RESEARCH CENTRE/TRANSFER'
        if re.search(sigma_pattern, narration):
            return "SIGMA TEST RESEARCH CENTRE"
        
        # Pattern 13: IFT with PANACE pattern
        # Format: IFT/BRANCH/AXOBR.../.../PANACE/...
        panace_pattern = r'IFT/BRANCH/[^/]+/[^/]+/PANACE/'
        if re.search(panace_pattern, narration):
            return "PANACE"
        
        # Pattern 14: NEFT with TOSHNIWAL TECHNOLOGIES pattern
        # Format: NEFT/.../TOSHNIWAL TECHNOLOGIES PVT L/PUNJAB NATIONAL BANK/...
        toshniwal_pattern = r'NEFT/[^/]+/TOSHNIWAL TECHNOLOGIES PVT L/PUNJAB NATIONAL BANK/'
        if re.search(toshniwal_pattern, narration):
            return "TOSHNIWAL TECHNOLOGIES PVT L"
        
        # Pattern 15: NEFT with TORRENT PHARMACEUTICALS pattern
        # Format: NEFT/.../TORRENT PHARMACEUTICALS LTD/HDFC BANK/...
        torrent_pattern = r'NEFT/[^/]+/TORRENT PHARMACEUTICALS LTD/HDFC BANK/'
        if re.search(torrent_pattern, narration):
            return "TORRENT PHARMACEUTICALS LTD"
        
        # Pattern 16: NEFT with HONDA CARS INDIA pattern (concatenated format)
        # Format: NEFT/.../HONDA CARS INDIA LTDHONDA CA/MUFG BANK/...
        honda_pattern = r'HONDA CARS INDIA LTDHONDA CA'
        if re.search(honda_pattern, narration):
            return "HONDA CARS INDIA LTD"
        
        # Pattern 17: RTGS with HONDA CARS INDIA pattern (concatenated format)
        # Format: RTGS/.../HONDA CARS INDIA LTDHO/MUFG BANK/...
        honda_rtgs_pattern = r'HONDA CARS INDIA LTDHO'
        if re.search(honda_rtgs_pattern, narration):
            return "HONDA CARS INDIA LTD"
        
        # Pattern 6: CLG (Clearing) transactions - these are usually bank names, not parties
        # Skip these as they're typically bank clearing transactions
        
        # Pattern 7: IMPS transactions - usually small amounts, often test transactions
        # Skip these as they're usually not meaningful business parties
        
        return None
    
    def is_valid_party_name(self, party_name):
        """
        Check if the extracted party name is valid and meaningful
        """
        if not party_name or len(party_name) < 3:
            return False
            
        # Skip common bank names and non-party identifiers
        # Note: LTD and LIMITED are legitimate business suffixes, not bank identifiers
        bank_keywords = [
            'BANK', 'PVT', 'PRIVATE', 'CORPORATION', 'CORP',
            'HDFC', 'ICICI', 'SBI', 'STATE BANK', 'PUNJAB NATIONAL', 'CANARA',
            'UNION BANK', 'YES BANK', 'KOTAK', 'AXIS', 'STANDARD CHARTERED',
            'CITI', 'HSBC', 'IDFC', 'IDBI', 'BARODA', 'INDIA', 'INDIAN',
            'OVERSEAS', 'CENTRAL', 'UCO', 'PUNJAB AND SIND', 'RATNAKAR',
            'APIBANKI', 'RATNAKAR', 'NAINITAL', 'INDUSIND', 'JP MORGAN',
            'MORGAN', 'CHASE', 'DEUTSCHE', 'BNP', 'PARIBAS', 'CREDIT SUISSE',
            'MUFG BANK', 'MIZUHO BANK', 'BANK OF AMERICA', 'BANK OF INDIA'
        ]
        
        party_upper = party_name.upper()
        for keyword in bank_keywords:
            if keyword in party_upper:
                return False
        
        # Skip if it's just numbers or special characters
        if re.match(r'^[0-9\s\-_\.]+$', party_name):
            return False
            
        # Skip if it's too short or looks like a reference number
        if len(party_name) < 5 or re.match(r'^[A-Z0-9]+$', party_name):
            return False
            
        return True
    
    def clean_party_name(self, party_name):
        """
        Clean and standardize party name
        """
        # Remove extra spaces and normalize
        party_name = re.sub(r'\s+', ' ', party_name.strip())
        
        # Remove common suffixes that don't add meaning
        suffixes_to_remove = [
            ' PVT LTD', ' PRIVATE LIMITED', ' LIMITED', ' LTD',
            ' PVT', ' PRIVATE', ' CORPORATION', ' CORP',
            ' INDIA', ' INDIAN', ' INTERNATIONAL'
        ]
        
        for suffix in suffixes_to_remove:
            if party_name.upper().endswith(suffix.upper()):
                party_name = party_name[:-len(suffix)]
                break
        
        return party_name.strip()
    
    def analyze_transactions(self):
        """
        Analyze all income transactions and categorize by party
        """
        print("🔍 Analyzing income transactions for party names...")
        
        # Read the income transactions file
        df = pd.read_csv(self.income_file_path)
        
        total_transactions = len(df)
        categorized_count = 0
        
        for index, row in df.iterrows():
            narration = row['narration']
            amount = row['amount']
            date = row['date']
            
            # Extract party name
            party_name = self.extract_party_name(narration)
            
            if party_name:
                # Categorize by party
                self.party_totals[party_name] += amount
                self.party_transactions[party_name].append({
                    'date': date,
                    'narration': narration,
                    'amount': amount
                })
                categorized_count += 1
            else:
                # Uncategorized transaction
                self.uncategorized_transactions.append({
                    'date': date,
                    'narration': narration,
                    'amount': amount
                })
        
        print(f"✅ Analysis complete!")
        print(f"   Total transactions: {total_transactions}")
        print(f"   Categorized transactions: {categorized_count}")
        print(f"   Uncategorized transactions: {len(self.uncategorized_transactions)}")
        print(f"   Unique parties found: {len(self.party_totals)}")
        
        return df
    
    def generate_party_summary(self, output_file=None):
        """
        Generate a comprehensive party-wise summary
        """
        if output_file is None:
            output_file = "data/summary/party_wise_income_summary.txt"
        
        # Sort parties by total amount (descending)
        sorted_parties = sorted(self.party_totals.items(), key=lambda x: x[1], reverse=True)
        

        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("AXIS BANK - PARTY WISE INCOME ANALYSIS\n")
            f.write("=" * 80 + "\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Source file: {self.income_file_path}\n\n")
            
            # Summary statistics
            total_categorized_amount = sum(self.party_totals.values())
            total_uncategorized_amount = sum(t['amount'] for t in self.uncategorized_transactions)
            total_amount = total_categorized_amount + total_uncategorized_amount
            
            f.write("📊 SUMMARY STATISTICS\n")
            f.write("-" * 40 + "\n")
            f.write(f"Total income amount: ₹{total_amount:,.2f}\n")
            f.write(f"Categorized amount: ₹{total_categorized_amount:,.2f} ({total_categorized_amount/total_amount*100:.1f}%)\n")
            f.write(f"Uncategorized amount: ₹{total_uncategorized_amount:,.2f} ({total_uncategorized_amount/total_amount*100:.1f}%)\n")
            f.write(f"Total parties identified: {len(self.party_totals)}\n")
            f.write(f"Total transactions: {sum(len(txs) for txs in self.party_transactions.values()) + len(self.uncategorized_transactions)}\n\n")
            
            # Party-wise breakdown
            f.write("🏢 PARTY WISE BREAKDOWN\n")
            f.write("-" * 40 + "\n")
            
            for i, (party_name, total_amount) in enumerate(sorted_parties, 1):
                transaction_count = len(self.party_transactions[party_name])
                percentage = (total_amount / total_categorized_amount) * 100
                
                f.write(f"{i:2d}. {party_name}\n")
                f.write(f"    Amount: ₹{total_amount:,.2f} ({percentage:.1f}%)\n")
                f.write(f"    Transactions: {transaction_count}\n")
                f.write(f"    Average per transaction: ₹{total_amount/transaction_count:,.2f}\n")
                f.write("\n")
            
            # Uncategorized transactions
            if self.uncategorized_transactions:
                f.write("❓ UNCATEGORIZED TRANSACTIONS\n")
                f.write("-" * 40 + "\n")
                f.write(f"Total amount: ₹{total_uncategorized_amount:,.2f}\n")
                f.write(f"Transaction count: {len(self.uncategorized_transactions)}\n\n")
                
                # Show some examples of uncategorized transactions
                f.write("Sample uncategorized transactions:\n")
                for i, tx in enumerate(self.uncategorized_transactions[:10], 1):
                    f.write(f"{i}. {tx['date']} - ₹{tx['amount']:,.2f} - {tx['narration'][:80]}...\n")
                
                if len(self.uncategorized_transactions) > 10:
                    f.write(f"... and {len(self.uncategorized_transactions) - 10} more transactions\n")
                f.write("\n")
            
            # Detailed transaction list for each party
            f.write("📋 DETAILED TRANSACTION LIST BY PARTY\n")
            f.write("=" * 80 + "\n")
            
            for party_name, total_amount in sorted_parties:
                f.write(f"\n🏢 {party_name} - Total: ₹{total_amount:,.2f}\n")
                f.write("-" * 60 + "\n")
                
                transactions = self.party_transactions[party_name]
                for tx in transactions:
                    f.write(f"{tx['date']} - ₹{tx['amount']:,.2f} - {tx['narration']}\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("END OF REPORT\n")
            f.write("=" * 80 + "\n")
        
        print(f"📄 Party summary saved to: {output_file}")
        return output_file
    
    def create_enhanced_csv(self, output_file=None):
        """
        Create an enhanced CSV with party names added
        """
        if output_file is None:
            output_file = "data/income/party/axis_income_with_parties.csv"
        
        # Read original file
        df = pd.read_csv(self.income_file_path)
        
        # Add party name column
        df['party_name'] = df['narration'].apply(self.extract_party_name)
        
        # Fill NaN with 'Uncategorized'
        df['party_name'] = df['party_name'].fillna('Uncategorized')
        

        
        # Save enhanced CSV
        df.to_csv(output_file, index=False)
        
        print(f"📊 Enhanced CSV with party names saved to: {output_file}")
        return output_file

def main():
    """Main function to run the party analysis"""
    income_file = "data/income/axis_income_transactions.csv"
    
    if not os.path.exists(income_file):
        print(f"❌ Error: Income file not found: {income_file}")
        return
    
    # Create analyzer
    analyzer = PartyAnalyzer(income_file)
    
    # Analyze transactions
    analyzer.analyze_transactions()
    
    # Generate party summary
    summary_file = analyzer.generate_party_summary()
    
    # Create enhanced CSV
    enhanced_csv = analyzer.create_enhanced_csv()
    
    print(f"\n🎉 Analysis complete! Check the generated files:")
    print(f"   📄 Summary: {summary_file}")
    print(f"   📊 Enhanced CSV: {enhanced_csv}")

if __name__ == "__main__":
    main()
