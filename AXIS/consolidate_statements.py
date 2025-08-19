#!/usr/bin/env python3
"""
AXIS Bank Statement Consolidator
Combines multiple AXIS bank statement CSV files into a single CSV output
"""

import pandas as pd
import os
import re
import shutil
import argparse
from datetime import datetime
import numpy as np
from pathlib import Path

class AXISStatementProcessor:
    
    def __init__(self, statements_directory):
        self.statements_dir = statements_directory
        self.consolidated_data = []
        
    def extract_account_info(self, file_path):
        """Extract account information from header rows"""
        account_info = {
            'account_number': None,
            'customer_name': None,
            'branch': None,
            'statement_period': None,
            'ifsc_code': None,
            'micr_code': None
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            # Extract customer name (line 1)
            if len(lines) > 0:
                name_line = lines[0].strip()
                if name_line.startswith('Name :-'):
                    account_info['customer_name'] = name_line.replace('Name :-', '').strip().rstrip('.')
            
            # Extract account number from statement line (around line 15)
            for line in lines:
                if 'Statement of Account No -' in line:
                    match = re.search(r'Statement of Account No - (\d+)', line)
                    if match:
                        account_info['account_number'] = match.group(1)
                    break
            
            # Extract statement period
            for line in lines:
                if 'Statement of Account No -' in line and 'for the period' in line:
                    match = re.search(r'for the period \(From : (\d{2}/\d{2}/\d{4}) To : (\d{2}/\d{2}/\d{4})\)', line)
                    if match:
                        account_info['statement_period'] = f"{match.group(1)} to {match.group(2)}"
                    break
            
            # Extract IFSC and MICR codes
            for line in lines:
                if 'IFSC Code :-' in line:
                    match = re.search(r'IFSC Code :- (\w+)', line)
                    if match:
                        account_info['ifsc_code'] = match.group(1)
                elif 'MICR Code :-' in line:
                    match = re.search(r'MICR Code :- (\d+)', line)
                    if match:
                        account_info['micr_code'] = match.group(1)
                        
        except Exception as e:
            print(f"Error extracting account info from {file_path}: {str(e)}")
            
        return account_info
    
    def clean_date(self, date_str):
        """Convert DD/MM/YYYY format to YYYY-MM-DD"""
        if pd.isna(date_str) or date_str == '' or str(date_str).strip() == '':
            return None
            
        try:
            date_str = str(date_str).strip()
            # Handle DD/MM/YYYY format
            if '/' in date_str and len(date_str.split('/')) == 3:
                day, month, year = date_str.split('/')
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        except:
            pass
        return None
    
    def clean_amount(self, amount_str):
        """Clean and convert amount strings to float"""
        if pd.isna(amount_str) or amount_str == '' or str(amount_str).strip() == '':
            return 0.0
            
        try:
            # Remove commas, tabs, and convert to float
            amount_str = str(amount_str).replace(',', '').replace('\t', '').strip()
            return float(amount_str)
        except:
            return 0.0
    
    def clean_balance(self, balance_str):
        """Clean balance strings (handle negative format with commas)"""
        if pd.isna(balance_str) or balance_str == '' or str(balance_str).strip() == '':
            return 0.0
            
        try:
            balance_str = str(balance_str).strip()
            # Remove commas and handle negative format
            balance_str = balance_str.replace(',', '')
            # Handle AXIS format like "-,93,43,827.31"
            if balance_str.startswith('-,'):
                balance_str = '-' + balance_str[2:]
            return float(balance_str)
        except:
            return 0.0
    
    def process_single_file(self, file_path):
        """Process a single AXIS statement file"""
        print(f"Processing: {os.path.basename(file_path)}")
        
        try:
            # Read the file as text first to handle embedded newlines
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Extract account information
            account_info = self.extract_account_info(file_path)
            
            # Find the header row (contains column names)
            header_row = None
            for i, line in enumerate(lines):
                if 'S.No' in line and 'Transaction Date' in line:
                    header_row = i
                    break
            
            if header_row is None:
                print(f"  Could not find header row in {file_path}")
                return []
            
            # Parse the CSV manually starting from header row
            transactions = []
            header_line = lines[header_row].strip()
            columns = header_line.split(',')
            
            # Process each line after the header
            for i in range(header_row + 1, len(lines)):
                line = lines[i].strip()
                if not line:
                    continue
                
                # Split by comma, but handle quoted fields properly
                fields = self.parse_csv_line(line)
                if len(fields) < 9:  # Need at least 9 columns
                    continue
                
                # Skip summary rows
                if 'TRANSACTION TOTAL' in fields[3] or 'CLOSING BALANCE' in fields[3]:
                    continue
                
                # Skip opening balance row
                if 'OPENING BALANCE' in fields[3]:
                    continue
                
                # Check if this is a valid transaction row
                date_str = fields[1].strip()  # Transaction Date
                if not date_str or date_str == '' or len(date_str) < 5:
                    continue
                
                # Clean the transaction data
                transaction = {
                    'account_number': account_info['account_number'],
                    'customer_name': account_info['customer_name'],
                    'date': self.clean_date(fields[1]),  # Transaction Date
                    'value_date': self.clean_date(fields[2]),  # Value Date
                    'narration': fields[3].strip() if len(fields) > 3 else '',  # Particulars
                    'amount': self.clean_amount(fields[4]),  # Amount(INR)
                    'debit_credit': fields[5].strip() if len(fields) > 5 else '',  # Debit/Credit
                    'balance': self.clean_balance(fields[6]),  # Balance(INR)
                    'cheque_number': fields[7].strip() if len(fields) > 7 else '',  # Cheque Number
                    'branch_name': fields[8].strip() if len(fields) > 8 else '',  # Branch Name
                    'source_file': os.path.basename(file_path)
                }
                
                # Determine transaction type and amounts
                if transaction['debit_credit'] == 'DR':
                    transaction['withdrawal_amount'] = transaction['amount']
                    transaction['deposit_amount'] = 0.0
                    transaction['transaction_type'] = 'Expense'
                elif transaction['debit_credit'] == 'CR':
                    transaction['withdrawal_amount'] = 0.0
                    transaction['deposit_amount'] = transaction['amount']
                    transaction['transaction_type'] = 'Income'
                else:
                    transaction['withdrawal_amount'] = 0.0
                    transaction['deposit_amount'] = 0.0
                    transaction['transaction_type'] = 'Unknown'
                
                # Generate reference number from narration
                transaction['reference_number'] = self.extract_reference_number(transaction['narration'])
                
                # Only add if we have a valid date
                if transaction['date']:
                    transactions.append(transaction)
            
            print(f"  Extracted {len(transactions)} transactions")
            return transactions
            
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
            return []
    
    def parse_csv_line(self, line):
        """Parse a CSV line, handling quoted fields and embedded commas"""
        fields = []
        current_field = ""
        in_quotes = False
        
        for char in line:
            if char == '"':
                in_quotes = not in_quotes
            elif char == ',' and not in_quotes:
                fields.append(current_field.strip())
                current_field = ""
            else:
                current_field += char
        
        # Add the last field
        fields.append(current_field.strip())
        return fields
    
    def extract_reference_number(self, narration):
        """Extract reference number from transaction narration"""
        if not narration:
            return ''
        
        # Look for common reference number patterns in AXIS statements
        patterns = [
            r'NEFT/([A-Z0-9]+)',  # NEFT reference
            r'IMPS/([A-Z0-9]+)',  # IMPS reference
            r'UPI/([A-Z0-9]+)',   # UPI reference
            r'CLG/(\d+)',         # Cheque clearing
            r'BRN-CLG-CHQ/(\d+)', # Branch cheque clearing
            r'AXOIC(\d+)',        # AXIS internal reference
        ]
        
        for pattern in patterns:
            match = re.search(pattern, narration)
            if match:
                return match.group(1)
        
        # If no specific pattern found, use first part of narration
        return narration[:20] if len(narration) > 20 else narration
    
    def process_all_files(self):
        """Process all CSV files in the statements directory"""
        csv_files = [f for f in os.listdir(self.statements_dir) 
                    if f.endswith('.CSV') or f.endswith('.csv')]
        
        print(f"Found {len(csv_files)} CSV files to process")
        
        all_transactions = []
        for file in csv_files:
            file_path = os.path.join(self.statements_dir, file)
            transactions = self.process_single_file(file_path)
            all_transactions.extend(transactions)
        
        return all_transactions
    
    def create_consolidated_csv(self, output_file='consolidated_axis_statements.csv'):
        """Create consolidated CSV from all bank statements"""
        print(f"\n{'='*60}")
        print("AXIS Bank Statement Consolidation")
        print(f"{'='*60}")
        
        # Process all files
        all_transactions = self.process_all_files()
        
        if not all_transactions:
            print("No transactions found to consolidate!")
            return
        
        # Create DataFrame
        df = pd.DataFrame(all_transactions)
        
        # Sort by date and account number
        df = df.sort_values(['account_number', 'date'], na_position='last')
        
        # Add sequential serial numbers
        df['serial_no'] = range(1, len(df) + 1)
        
        # Add net transaction column (deposit - withdrawal)
        df['net_transaction'] = df['deposit_amount'] - df['withdrawal_amount']
        
        # Add account name mapping
        account_mapping = {
            '922030048910705': 'AXIS Primary',
            # Add more account mappings as needed
        }
        
        df['account_name'] = df['account_number'].map(account_mapping).fillna('Unknown')
        
        # Detect inter-bank transactions vs unique transactions
        # Group by reference_number and calculate stats
        ref_stats = df.groupby('reference_number').agg({
            'net_transaction': ['sum', 'count'],
            'account_number': 'nunique'
        }).reset_index()
        ref_stats.columns = ['reference_number', 'net_sum', 'count', 'unique_accounts']
        
        # Merge back to main dataframe
        df = df.merge(ref_stats, on='reference_number', how='left')
        
        # Helper function to find reversal groups within a set of transactions
        def find_reversal_groups(transactions):
            """
            Efficiently find subsets of transactions that sum to approximately 0.
            Returns indices of transactions that form reversal groups.
            """
            amounts = transactions['net_transaction'].values
            indices = list(range(len(amounts)))
            
            if len(amounts) <= 1:
                return []
            
            # For 2 transactions, check if they approximately cancel out
            if len(amounts) == 2:
                if abs(amounts[0] + amounts[1]) < 0.01:
                    return [0, 1]
                return []
            
            # For larger sets, use efficient approach
            from itertools import combinations
            tolerance = 0.01
            
            # Check pairs first (most common case)
            for i in range(len(amounts)):
                for j in range(i + 1, len(amounts)):
                    if abs(amounts[i] + amounts[j]) < tolerance:
                        return [i, j]
            
            # Check triplets (second most common)
            if len(amounts) <= 10:
                for combo in combinations(indices, 3):
                    combo_sum = sum(amounts[i] for i in combo)
                    if abs(combo_sum) < tolerance:
                        return list(combo)
            
            return []
        
        # Add helper columns to track reversal classification
        df['temp_classification'] = 'Unique'
        df['temp_reversal_group'] = False
        
        # Process each reference number separately
        unique_refs = df['reference_number'].unique()
        total_refs = len(unique_refs)
        print(f"🔄 Processing {total_refs} unique reference numbers for reversal detection...")
        
        for idx, ref_num in enumerate(unique_refs):
            if idx % 100 == 0 and idx > 0:
                print(f"   Processed {idx}/{total_refs} reference numbers ({idx/total_refs*100:.1f}%)")
            
            ref_transactions = df[df['reference_number'] == ref_num]
            
            if len(ref_transactions) == 1:
                # Single transaction - always Unique
                continue
            elif ref_transactions['account_number'].nunique() > 1:
                # Multiple accounts - check for inter-bank transfers
                if abs(ref_transactions['net_transaction'].sum()) < 0.01:
                    df.loc[df['reference_number'] == ref_num, 'temp_classification'] = 'Inter-bank'
            else:
                # Same account, multiple transactions
                reversal_indices = find_reversal_groups(ref_transactions)
                
                if reversal_indices:
                    # Mark reversal group transactions
                    ref_indices = ref_transactions.index[reversal_indices]
                    df.loc[ref_indices, 'temp_classification'] = 'Reversed'
                    df.loc[ref_indices, 'temp_reversal_group'] = True
        
        # Apply the classification
        df['transaction_classification'] = df['temp_classification']
        
        # Clean up temporary columns
        df = df.drop(['temp_classification', 'temp_reversal_group'], axis=1)
        
        # Drop the helper columns
        df = df.drop(['net_sum', 'count', 'unique_accounts'], axis=1)
        
        # Reorder columns for better readability
        column_order = [
            'serial_no', 'account_name', 'account_number', 'date', 'value_date', 'narration', 
            'reference_number', 'transaction_type', 'transaction_classification', 
            'withdrawal_amount', 'deposit_amount', 'net_transaction', 'balance', 
            'debit_credit', 'cheque_number', 'branch_name', 'source_file'
        ]
        
        # Only include columns that exist in the dataframe
        final_columns = [col for col in column_order if col in df.columns]
        df = df[final_columns]
        
        # Save to CSV
        output_path = os.path.join(os.path.dirname(self.statements_dir), output_file)
        df.to_csv(output_path, index=False)
        
        # Generate comprehensive summary
        summary_lines = self.generate_comprehensive_summary(df, output_path)
        
        # Print to console
        for line in summary_lines:
            print(line)
        
        # Save summary to text file
        summary_file = os.path.join(os.path.dirname(self.statements_dir), 'consolidation_summary.txt')
        with open(summary_file, 'w') as f:
            f.write('\n'.join(summary_lines))
        
        print(f"\n📋 Detailed summary saved to: {summary_file}")
        
        # Show sample data
        print(f"\nSample data (first 5 rows):")
        print(df.head().to_string(index=False))
        
        return output_path
    
    def generate_comprehensive_summary(self, df, output_path):
        """Generate comprehensive summary for console and file output"""
        from datetime import datetime
        
        lines = []
        lines.append("=" * 80)
        lines.append("AXIS BANK STATEMENT CONSOLIDATION - COMPREHENSIVE SUMMARY")
        lines.append("=" * 80)
        lines.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Output file: {output_path}")
        lines.append("")
        
        # Processing Summary
        lines.append("📁 PROCESSING SUMMARY")
        lines.append("-" * 40)
        csv_files = [f for f in os.listdir(self.statements_dir) 
                    if f.endswith('.CSV') or f.endswith('.csv')]
        lines.append(f"Files processed: {len(csv_files)}")
        lines.append(f"Total transactions extracted: {len(df)}")
        lines.append("")
        
        # Date Range Analysis
        lines.append("📅 DATE RANGE ANALYSIS")
        lines.append("-" * 40)
        min_date = df['date'].min()
        max_date = df['date'].max()
        lines.append(f"Period: {min_date} to {max_date}")
        
        # Calculate period duration
        from datetime import datetime
        start_date = datetime.strptime(min_date, '%Y-%m-%d')
        end_date = datetime.strptime(max_date, '%Y-%m-%d')
        period_days = (end_date - start_date).days
        lines.append(f"Duration: {period_days} days ({period_days/30.44:.1f} months)")
        lines.append("")
        
        # Account Summary
        lines.append("🏦 ACCOUNT SUMMARY")
        lines.append("-" * 40)
        lines.append(f"Total unique accounts: {df['account_number'].nunique()}")
        
        account_summary = df.groupby(['account_number', 'account_name']).size().reset_index(name='transaction_count')
        for _, row in account_summary.iterrows():
            lines.append(f"  {row['account_name']} ({row['account_number']}): {row['transaction_count']} transactions")
        lines.append("")
        
        # Transaction Type Breakdown
        lines.append("💰 TRANSACTION TYPE BREAKDOWN")
        lines.append("-" * 40)
        type_counts = df['transaction_type'].value_counts()
        total_income = df[df['transaction_type'] == 'Income']['deposit_amount'].sum()
        total_expenses = df[df['transaction_type'] == 'Expense']['withdrawal_amount'].sum()
        
        # External transactions only (for true business performance)
        external_df = df[df['transaction_classification'] == 'Unique']
        external_type_counts = external_df['transaction_type'].value_counts()
        external_income = external_df[external_df['transaction_type'] == 'Income']['deposit_amount'].sum()
        external_expenses = external_df[external_df['transaction_type'] == 'Expense']['withdrawal_amount'].sum()
        
        lines.append(f"Total Income transactions: {type_counts.get('Income', 0)} (₹{total_income:,.2f})")
        lines.append(f"Total Expense transactions: {type_counts.get('Expense', 0)} (₹{total_expenses:,.2f})")
        lines.append(f"External Income transactions: {external_type_counts.get('Income', 0)} (₹{external_income:,.2f})")
        lines.append(f"External Expense transactions: {external_type_counts.get('Expense', 0)} (₹{external_expenses:,.2f})")
        lines.append(f"True business profit/loss: ₹{external_income - external_expenses:,.2f}")
        lines.append("")
        
        # Transaction Classification
        lines.append("🔄 TRANSACTION CLASSIFICATION")
        lines.append("-" * 40)
        classification_counts = df['transaction_classification'].value_counts()
        lines.append(f"Unique transactions: {classification_counts.get('Unique', 0)} (external business transactions)")
        lines.append(f"Inter-bank transfers: {classification_counts.get('Inter-bank', 0)} (transfers between accounts)")
        lines.append(f"Reversed transactions: {classification_counts.get('Reversed', 0)} (failed/cancelled payments)")
        lines.append("")
        
        # Financial Summary by Account (EXCLUDING inter-bank transactions)
        lines.append("📊 FINANCIAL SUMMARY BY ACCOUNT (External Transactions Only)")
        lines.append("-" * 40)
        lines.append(f"{'Account':<15} | {'Txns':<5} | {'Income (₹)':<15} | {'Expenses (₹)':<15} | {'Net (₹)':<15}")
        lines.append("-" * 80)
        
        # Filter out inter-bank transactions for true business performance
        external_df = df[df['transaction_classification'] == 'Unique']
        
        total_external_income = 0
        total_external_expenses = 0
        total_external_txns = 0
        
        for account_name in df['account_name'].unique():
            account_data = external_df[external_df['account_name'] == account_name]
            if len(account_data) > 0:
                acc_income = account_data[account_data['transaction_type'] == 'Income']['deposit_amount'].sum()
                acc_expenses = account_data[account_data['transaction_type'] == 'Expense']['withdrawal_amount'].sum()
                acc_net = acc_income - acc_expenses
                lines.append(f"{account_name:<15} | {len(account_data):<5} | {acc_income:<15,.2f} | {acc_expenses:<15,.2f} | {acc_net:<15,.2f}")
                
                total_external_income += acc_income
                total_external_expenses += acc_expenses
                total_external_txns += len(account_data)
        
        lines.append("-" * 80)
        lines.append(f"{'TOTAL':<15} | {total_external_txns:<5} | {total_external_income:<15,.2f} | {total_external_expenses:<15,.2f} | {total_external_income - total_external_expenses:<15,.2f}")
        lines.append("")
        
        # Key Insights
        lines.append("🎯 KEY INSIGHTS")
        lines.append("-" * 40)
        
        # Most active account (all transactions)
        most_active = df['account_name'].value_counts().index[0]
        most_active_count = df['account_name'].value_counts().iloc[0]
        lines.append(f"Most active account: {most_active} ({most_active_count} transactions)")
        
        # Highest external income account
        external_account_income = external_df[external_df['transaction_type'] == 'Income'].groupby('account_name')['deposit_amount'].sum()
        if len(external_account_income) > 0:
            highest_income_account = external_account_income.idxmax()
            highest_income_amount = external_account_income.max()
            lines.append(f"Highest external income account: {highest_income_account} (₹{highest_income_amount:,.2f})")
        
        # Highest external expense account
        external_account_expenses = external_df[external_df['transaction_type'] == 'Expense'].groupby('account_name')['withdrawal_amount'].sum()
        if len(external_account_expenses) > 0:
            highest_expense_account = external_account_expenses.idxmax()
            highest_expense_amount = external_account_expenses.max()
            lines.append(f"Highest external expense account: {highest_expense_account} (₹{highest_expense_amount:,.2f})")
        
        # Inter-bank and reversed transaction insights
        interbank_amount = df[df['transaction_classification'] == 'Inter-bank']['net_transaction'].abs().sum() / 2
        reversed_amount = df[df['transaction_classification'] == 'Reversed']['net_transaction'].abs().sum() / 2
        lines.append(f"Total inter-bank transfer volume: ₹{interbank_amount:,.2f}")
        lines.append(f"Total reversed transaction volume: ₹{reversed_amount:,.2f}")
        
        # True business performance (external only)
        true_business_profit = external_income - external_expenses
        if true_business_profit > 0:
            lines.append(f"True business profit (external only): ₹{true_business_profit:,.2f}")
        elif true_business_profit < 0:
            lines.append(f"True business loss (external only): ₹{abs(true_business_profit):,.2f}")
        else:
            lines.append("True business performance: Break-even")
        
        lines.append("")
        lines.append("=" * 80)
        lines.append("END OF SUMMARY")
        lines.append("=" * 80)
        
        return lines
    
    def copy_to_desktop(self, output_files):
        """Copy output files to a timestamped directory on the desktop"""
        try:
            # Get desktop path
            desktop_path = Path.home() / "Desktop"
            
            # Create timestamped directory name
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            desktop_dir = desktop_path / f"axis_statement_consolidated_{timestamp}"
            
            # Create the directory
            desktop_dir.mkdir(parents=True, exist_ok=True)
            
            copied_files = []
            for file_path in output_files:
                if os.path.exists(file_path):
                    file_name = os.path.basename(file_path)
                    destination = desktop_dir / file_name
                    shutil.copy2(file_path, destination)
                    copied_files.append(str(destination))
                    print(f"📋 Copied {file_name} to: {destination}")
            
            print(f"\n📁 All files copied to desktop directory: {desktop_dir}")
            return str(desktop_dir), copied_files
            
        except Exception as e:
            print(f"❌ Error copying files to desktop: {str(e)}")
            return None, []

def main():
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='AXIS Bank Statement Consolidator')
    parser.add_argument(
        '--statements-dir',
        type=str,
        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'statements'),
        help='Directory containing AXIS bank statement CSV files (default: ./data/statements)'
    )
    parser.add_argument(
        '--no-desktop-copy',
        action='store_true',
        help='Skip copying files to desktop directory'
    )
    
    args = parser.parse_args()
    
    # Validate statements directory
    if not os.path.exists(args.statements_dir):
        print(f"❌ Error: Statements directory not found: {args.statements_dir}")
        print("Please ensure the directory exists and contains CSV files.")
        return
    
    # Check if directory has CSV files
    csv_files = [f for f in os.listdir(args.statements_dir) 
                if f.endswith('.CSV') or f.endswith('.csv')]
    if not csv_files:
        print(f"❌ Error: No CSV files found in: {args.statements_dir}")
        print("Please ensure the directory contains AXIS bank statement CSV files.")
        return
    
    print(f"📂 Using statements directory: {args.statements_dir}")
    print(f"📊 Found {len(csv_files)} CSV files to process")
    
    # Process statements
    processor = AXISStatementProcessor(args.statements_dir)
    output_file = processor.create_consolidated_csv()
    
    if output_file:
        print(f"\n✅ Consolidation completed successfully!")
        print(f"📁 Output file: {output_file}")
        
        # Determine the summary file path
        summary_file = os.path.join(os.path.dirname(args.statements_dir), 'consolidation_summary.txt')
        
        # Copy to desktop if not disabled
        if not args.no_desktop_copy:
            output_files = [output_file]
            if os.path.exists(summary_file):
                output_files.append(summary_file)
            
            desktop_dir, copied_files = processor.copy_to_desktop(output_files)
            if desktop_dir and copied_files:
                print(f"🎉 Files successfully copied to desktop: {desktop_dir}")
    else:
        print(f"❌ Consolidation failed!")

if __name__ == "__main__":
    main()
