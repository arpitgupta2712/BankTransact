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
        self.data_dir = Path(statements_directory).parent
        
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
            # Remove quotes if present
            balance_str = balance_str.strip('"').strip("'")
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
                
                # Use cheque number as reference number if available, otherwise null
                transaction['reference_number'] = transaction['cheque_number'] if transaction['cheque_number'] else ''
                
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
        """Process all CSV files in the statements directory with intelligent deduplication"""
        csv_files = [f for f in os.listdir(self.statements_dir) 
                    if f.endswith('.CSV') or f.endswith('.csv')]
        
        print(f"Found {len(csv_files)} CSV files to process")
        
        # First, analyze all files to understand their periods and coverage
        file_analysis = self.analyze_statement_files(csv_files)
        
        # Sort files by coverage priority (most comprehensive first)
        prioritized_files = self.prioritize_files_by_coverage(file_analysis)
        
        print(f"\n📊 Statement Period Analysis:")
        for file_info in prioritized_files:
            print(f"  {file_info['filename']}: {file_info['start_date']} to {file_info['end_date']} ({file_info['duration_days']} days, {file_info['transaction_count']} transactions)")
        
        # Process files in priority order with deduplication
        all_transactions = self.process_files_with_deduplication(prioritized_files)
        
        return all_transactions
    
    def analyze_statement_files(self, csv_files):
        """Analyze all statement files to understand their periods and coverage"""
        file_analysis = []
        
        for file in csv_files:
            file_path = os.path.join(self.statements_dir, file)
            try:
                # Extract account info and period
                account_info = self.extract_account_info(file_path)
                
                # Get a sample of transactions to estimate count
                sample_transactions = self.process_single_file(file_path)
                
                # Parse dates
                start_date = None
                end_date = None
                if account_info['statement_period']:
                    # Extract dates from period string like "01/08/2025 to 03/08/2025"
                    period_match = re.search(r'(\d{2}/\d{2}/\d{4})\s+to\s+(\d{2}/\d{2}/\d{4})', account_info['statement_period'])
                    if period_match:
                        start_date = self.clean_date(period_match.group(1))
                        end_date = self.clean_date(period_match.group(2))
                
                # Calculate duration
                duration_days = 0
                if start_date and end_date:
                    from datetime import datetime
                    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                    duration_days = (end_dt - start_dt).days + 1
                
                file_analysis.append({
                    'filename': file,
                    'file_path': file_path,
                    'account_number': account_info['account_number'],
                    'start_date': start_date,
                    'end_date': end_date,
                    'duration_days': duration_days,
                    'transaction_count': len(sample_transactions),
                    'account_info': account_info
                })
                
            except Exception as e:
                print(f"Error analyzing {file}: {str(e)}")
                continue
        
        return file_analysis
    
    def prioritize_files_by_coverage(self, file_analysis):
        """Prioritize files by coverage - most comprehensive first"""
        # Sort by duration (longest first), then by transaction count (highest first)
        prioritized = sorted(file_analysis, 
                           key=lambda x: (x['duration_days'], x['transaction_count']), 
                           reverse=True)
        return prioritized
    
    def process_files_with_deduplication(self, prioritized_files):
        """Process files in priority order with intelligent deduplication"""
        all_transactions = []
        processed_transaction_keys = set()  # Track unique transaction identifiers
        
        print(f"\n🔄 Processing files with deduplication:")
        
        for file_info in prioritized_files:
            file_path = file_info['file_path']
            filename = file_info['filename']
            
            print(f"\nProcessing: {filename}")
            print(f"  Period: {file_info['start_date']} to {file_info['end_date']} ({file_info['duration_days']} days)")
            
            # Get all transactions from this file
            file_transactions = self.process_single_file(file_path)
            
            # Filter out duplicate transactions
            new_transactions = []
            skipped_count = 0
            
            for transaction in file_transactions:
                # Create a unique key for this transaction
                transaction_key = self.create_transaction_key(transaction)
                
                if transaction_key not in processed_transaction_keys:
                    new_transactions.append(transaction)
                    processed_transaction_keys.add(transaction_key)
                else:
                    skipped_count += 1
                    print(f"    Skipping duplicate transaction: {transaction['date']} - {transaction['narration'][:50]}...")
            
            print(f"  Added {len(new_transactions)} new transactions (skipped {skipped_count} duplicates)")
            all_transactions.extend(new_transactions)
        
        print(f"\n✅ Total unique transactions after deduplication: {len(all_transactions)}")
        return all_transactions
    
    def create_transaction_key(self, transaction):
        """Create a unique key for a transaction to identify duplicates"""
        # Combine multiple fields to create a unique identifier
        key_parts = [
            transaction['date'],
            transaction['narration'][:100],  # First 100 chars of narration
            str(transaction['amount']),
            transaction['debit_credit'],
            transaction['cheque_number'] if transaction['cheque_number'] else ''
        ]
        return '|'.join(key_parts)
    
    def create_consolidated_csv(self, output_file='consolidated_axis_statements.csv'):
        """Create consolidated CSV from all bank statements"""
        print(f"\n{'='*60}")
        print("AXIS Bank Statement Consolidation")
        print(f"{'='*60}")
        
        # Create organized output directories
        self.create_output_directories()
        
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
        
        # Clean up and reorder columns for better readability
        column_order = [
            'serial_no', 'account_name', 'account_number', 'date', 'value_date', 'narration', 
            'reference_number', 'transaction_type', 'transaction_classification', 
            'withdrawal_amount', 'deposit_amount', 'net_transaction', 'balance', 
            'debit_credit'
        ]
        
        # Only include columns that exist in the dataframe
        final_columns = [col for col in column_order if col in df.columns]
        df = df[final_columns]
        
        # Save to CSV with clean naming
        output_path = self.consolidated_dir / 'consolidated_axis_statements.csv'
        df.to_csv(output_path, index=False)
        
        # Create separate income and expense CSV files
        self.create_separate_income_expense_files(df)
        
        # Perform balance verification
        verification_results = self.verify_balance_integrity(df)
        
        # Generate comprehensive summary
        summary_lines = self.generate_comprehensive_summary(df, output_path, verification_results)
        
        # Print to console
        for line in summary_lines:
            print(line)
        
        # Save summary to text file
        summary_file = self.summary_dir / 'consolidation_summary.txt'
        with open(summary_file, 'w') as f:
            f.write('\n'.join(summary_lines))
        
        print(f"\n📋 Detailed summary saved to: {summary_file}")
        
        # Show sample data
        print(f"\nSample data (first 5 rows):")
        print(df.head().to_string(index=False))
        
        return output_path
    
    def create_separate_income_expense_files(self, df):
        """Create separate CSV files for income and expense transactions"""
        # Define the columns for the simplified files (removed cheque_number since it's in reference_number)
        simplified_columns = ['account_number', 'date', 'narration', 'amount', 'transaction_type', 'transaction_classification']
        
        # Create income file
        income_df = df[df['transaction_type'] == 'Income'].copy()
        if len(income_df) > 0:
            # Add amount column (deposit amount for income)
            income_df['amount'] = income_df['deposit_amount']
            income_file = self.income_dir / 'axis_income_transactions.csv'
            income_df[simplified_columns].to_csv(income_file, index=False)
            print(f"📈 Income transactions saved to: {income_file}")
        
        # Create expense file
        expense_df = df[df['transaction_type'] == 'Expense'].copy()
        if len(expense_df) > 0:
            # Add amount column (withdrawal amount for expenses)
            expense_df['amount'] = expense_df['withdrawal_amount']
            expense_file = self.expense_dir / 'axis_expense_transactions.csv'
            expense_df[simplified_columns].to_csv(expense_file, index=False)
            print(f"📉 Expense transactions saved to: {expense_file}")
        
        print(f"✅ Created separate income ({len(income_df)}) and expense ({len(expense_df)}) files")
    
    def generate_comprehensive_summary(self, df, output_path, verification_results=None):
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
        
        # Add balance verification results if available
        if verification_results:
            lines.append("")
            lines.append("🔍 BALANCE INTEGRITY VERIFICATION")
            lines.append("-" * 40)
            lines.append(f"Verification Status: {verification_results['verification_status']}")
            
            if verification_results['verification_status'] == 'PASSED':
                lines.append("✅ Balance verification PASSED - No significant discrepancy")
            else:
                lines.append("❌ Balance verification FAILED - Significant discrepancy detected")
            
            lines.append("")
            lines.append("Balance Details:")
            if verification_results['opening_balance'] is not None:
                lines.append(f"  Opening Balance: ₹{verification_results['opening_balance']:,.2f}")
            else:
                lines.append(f"  Opening Balance: Not available")
            
            if verification_results['closing_balance'] is not None:
                lines.append(f"  Closing Balance: ₹{verification_results['closing_balance']:,.2f}")
            else:
                lines.append(f"  Closing Balance: Not available")
            
            if verification_results['calculated_balance'] is not None:
                lines.append(f"  Calculated Balance: ₹{verification_results['calculated_balance']:,.2f}")
            else:
                lines.append(f"  Calculated Balance: Not available")
            
            if verification_results['difference'] is not None:
                lines.append(f"  Difference: ₹{verification_results['difference']:,.2f} ({verification_results['difference_percentage']:.4f}%)")
            else:
                lines.append(f"  Difference: Not available")
            lines.append("")
            lines.append("Transaction Impact:")
            lines.append(f"  Total Income: ₹{verification_results['total_income']:,.2f}")
            lines.append(f"  Total Expenses: ₹{verification_results['total_expenses']:,.2f}")
            lines.append(f"  Net Impact: ₹{verification_results['net_impact']:,.2f}")
            if verification_results['expected_change'] is not None:
                lines.append(f"  Expected Change: ₹{verification_results['expected_change']:,.2f}")
            else:
                lines.append(f"  Expected Change: Not available")
            
            if verification_results['issues']:
                lines.append("")
                lines.append("Issues Detected:")
                for issue in verification_results['issues']:
                    lines.append(f"  ⚠️ {issue}")
            
            lines.append("")
            lines.append("Source Files Used:")
            for info in verification_results['source_files_info']:
                lines.append(f"  📄 {info}")
        
        lines.append("")
        lines.append("=" * 80)
        lines.append("END OF SUMMARY")
        lines.append("=" * 80)
        
        return lines
    
    def verify_balance_integrity(self, df):
        """Verify balance integrity by comparing calculated vs actual balances"""
        print(f"\n🔍 BALANCE INTEGRITY VERIFICATION")
        print(f"{'='*60}")
        
        # Get the prioritized files to find opening and closing balances
        csv_files = [f for f in os.listdir(self.statements_dir) 
                    if f.endswith('.CSV') or f.endswith('.csv')]
        file_analysis = self.analyze_statement_files(csv_files)
        prioritized_files = self.prioritize_files_by_coverage(file_analysis)
        
        # Find the earliest and latest dates in our consolidated data
        earliest_date = df['date'].min()
        latest_date = df['date'].max()
        
        print(f"Consolidated data period: {earliest_date} to {latest_date}")
        
        # Extract opening and closing balances from source statements
        opening_balance = None
        closing_balance = None
        source_files_info = []
        
        # Find opening balance from the file that covers the earliest date
        for file_info in prioritized_files:
            file_path = file_info['file_path']
            filename = file_info['filename']
            start_date = file_info['start_date']
            end_date = file_info['end_date']
            
            # Check if this file covers our earliest date (for opening balance)
            if start_date and start_date <= earliest_date and end_date and end_date >= earliest_date:
                file_opening = self.extract_opening_balance(file_path)
                if file_opening is not None:
                    opening_balance = file_opening
                    source_files_info.append(f"Opening balance from {filename}: ₹{opening_balance:,.2f}")
                    print(f"📊 Opening balance from {filename}: ₹{opening_balance:,.2f}")
                    break
        
        # Find closing balance from the file that covers the latest date
        for file_info in prioritized_files:
            file_path = file_info['file_path']
            filename = file_info['filename']
            start_date = file_info['start_date']
            end_date = file_info['end_date']
            
            # Check if this file covers our latest date (for closing balance)
            if start_date and start_date <= latest_date and end_date and end_date >= latest_date:
                file_closing = self.extract_closing_balance(file_path)
                if file_closing is not None:
                    closing_balance = file_closing
                    source_files_info.append(f"Closing balance from {filename}: ₹{closing_balance:,.2f}")
                    print(f"📊 Closing balance from {filename}: ₹{closing_balance:,.2f}")
                    break
        
        if opening_balance is None or closing_balance is None:
            print("⚠️  Could not extract opening or closing balance from source files")
            return {
                'verification_status': 'FAILED',
                'error': 'Could not extract opening or closing balance',
                'opening_balance': opening_balance,
                'closing_balance': closing_balance,
                'calculated_balance': None,
                'difference': None,
                'difference_percentage': 0,
                'total_income': 0,
                'total_expenses': 0,
                'net_impact': 0,
                'expected_change': 0,
                'issues': ['Could not extract opening or closing balance'],
                'source_files_info': source_files_info,
                'balance_tracking': []
            }
        
        # Calculate cumulative balance from our consolidated transactions
        # Sort by date to ensure proper chronological order
        df_sorted = df.sort_values('date')
        
        # Start with opening balance
        cumulative_balance = opening_balance
        balance_tracking = []
        
        print(f"\n📈 Balance Calculation:")
        print(f"Starting balance: ₹{cumulative_balance:,.2f}")
        
        # Process each transaction chronologically
        for _, transaction in df_sorted.iterrows():
            if transaction['transaction_type'] == 'Income':
                cumulative_balance += transaction['deposit_amount']
            elif transaction['transaction_type'] == 'Expense':
                cumulative_balance -= transaction['withdrawal_amount']
            
            # Track balance for verification
            balance_tracking.append({
                'date': transaction['date'],
                'transaction_type': transaction['transaction_type'],
                'amount': transaction['deposit_amount'] if transaction['transaction_type'] == 'Income' else transaction['withdrawal_amount'],
                'running_balance': cumulative_balance
            })
        
        print(f"Final calculated balance: ₹{cumulative_balance:,.2f}")
        print(f"Expected closing balance: ₹{closing_balance:,.2f}")
        
        # Calculate difference
        difference = cumulative_balance - closing_balance
        difference_percentage = (abs(difference) / abs(closing_balance)) * 100 if closing_balance != 0 else 0
        
        print(f"Difference: ₹{difference:,.2f} ({difference_percentage:.4f}%)")
        
        # Determine verification status
        if abs(difference) < 1.0:  # Allow for rounding differences up to ₹1
            verification_status = 'PASSED'
            print(f"✅ Balance verification PASSED - No significant discrepancy")
        else:
            verification_status = 'FAILED'
            print(f"❌ Balance verification FAILED - Significant discrepancy detected")
        
        # Detailed analysis
        print(f"\n📊 DETAILED ANALYSIS:")
        
        # Summary of transactions
        total_income = df[df['transaction_type'] == 'Income']['deposit_amount'].sum()
        total_expenses = df[df['transaction_type'] == 'Expense']['withdrawal_amount'].sum()
        
        print(f"Total income transactions: ₹{total_income:,.2f}")
        print(f"Total expense transactions: ₹{total_expenses:,.2f}")
        print(f"Net transaction impact: ₹{total_income - total_expenses:,.2f}")
        print(f"Expected change: ₹{closing_balance - opening_balance:,.2f}")
        
        # Check for potential issues
        issues = []
        if abs(difference) > 1.0:
            issues.append(f"Balance discrepancy of ₹{difference:,.2f}")
        
        if len(df) == 0:
            issues.append("No transactions found in consolidated data")
        
        # Check for missing transactions by comparing with source files
        source_transaction_counts = {}
        for file_info in prioritized_files:
            file_path = file_info['file_path']
            filename = file_info['filename']
            source_count = self.count_transactions_in_file(file_path)
            source_transaction_counts[filename] = source_count
        
        print(f"\n📋 Source file transaction counts:")
        for filename, count in source_transaction_counts.items():
            print(f"  {filename}: {count} transactions")
        
        return {
            'verification_status': verification_status,
            'opening_balance': opening_balance,
            'closing_balance': closing_balance,
            'calculated_balance': cumulative_balance,
            'difference': difference,
            'difference_percentage': difference_percentage,
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_impact': total_income - total_expenses,
            'expected_change': closing_balance - opening_balance,
            'issues': issues,
            'source_files_info': source_files_info,
            'balance_tracking': balance_tracking
        }
    
    def extract_opening_balance(self, file_path):
        """Extract opening balance from a statement file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line in lines:
                if 'OPENING BALANCE' in line:
                    fields = self.parse_csv_line(line)
                    if len(fields) >= 7:
                        balance_str = fields[6].strip()  # Balance is in field 7 (index 6)
                        balance = self.clean_balance(balance_str)
                        if balance is not None:
                            print(f"    Found opening balance: {balance_str} -> ₹{balance:,.2f}")
                            return balance
                        else:
                            print(f"    Could not parse opening balance: {balance_str}")
            print(f"    No opening balance found in {os.path.basename(file_path)}")
            return None
        except Exception as e:
            print(f"Error extracting opening balance from {file_path}: {str(e)}")
            return None
    
    def extract_closing_balance(self, file_path):
        """Extract closing balance from a statement file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line in lines:
                if 'CLOSING BALANCE' in line:
                    fields = self.parse_csv_line(line)
                    if len(fields) >= 7:
                        balance_str = fields[6].strip()  # Balance is in field 7 (index 6)
                        balance = self.clean_balance(balance_str)
                        if balance is not None:
                            print(f"    Found closing balance: {balance_str} -> ₹{balance:,.2f}")
                            return balance
                        else:
                            print(f"    Could not parse closing balance: {balance_str}")
            print(f"    No closing balance found in {os.path.basename(file_path)}")
            return None
        except Exception as e:
            print(f"Error extracting closing balance from {file_path}: {str(e)}")
            return None
    
    def count_transactions_in_file(self, file_path):
        """Count actual transactions in a source file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Find header row
            header_row = None
            for i, line in enumerate(lines):
                if 'S.No' in line and 'Transaction Date' in line:
                    header_row = i
                    break
            
            if header_row is None:
                return 0
            
            # Count transaction rows
            transaction_count = 0
            for i in range(header_row + 1, len(lines)):
                line = lines[i].strip()
                if not line:
                    continue
                
                fields = self.parse_csv_line(line)
                if len(fields) < 9:
                    continue
                
                # Skip summary rows
                if 'TRANSACTION TOTAL' in fields[3] or 'CLOSING BALANCE' in fields[3] or 'OPENING BALANCE' in fields[3]:
                    continue
                
                # Check if this is a valid transaction row
                date_str = fields[1].strip()
                if date_str and len(date_str) >= 5:
                    transaction_count += 1
            
            return transaction_count
        except Exception as e:
            print(f"Error counting transactions in {file_path}: {str(e)}")
            return 0
    
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

    def create_output_directories(self):
        """Create organized output directory structure"""
        # Create main output directories
        self.consolidated_dir = self.data_dir / "consolidated"
        self.income_dir = self.data_dir / "income"
        self.income_party_dir = self.income_dir / "party"
        self.expense_dir = self.data_dir / "expense"
        self.summary_dir = self.data_dir / "summary"
        
        # Create directories
        self.consolidated_dir.mkdir(exist_ok=True)
        self.income_dir.mkdir(exist_ok=True)
        self.income_party_dir.mkdir(exist_ok=True)
        self.expense_dir.mkdir(exist_ok=True)
        self.summary_dir.mkdir(exist_ok=True)
        
        print(f"📁 Created output directory structure:")
        print(f"   📂 Consolidated: {self.consolidated_dir}")
        print(f"   📂 Income: {self.income_dir}")
        print(f"   📂 Income/Party: {self.income_party_dir}")
        print(f"   📂 Expense: {self.expense_dir}")
        print(f"   📂 Summary: {self.summary_dir}")

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
        data_dir = os.path.dirname(args.statements_dir)
        summary_file = os.path.join(data_dir, 'summary', 'consolidation_summary.txt')
        
        # Skip desktop copy here - will be done at end of workflow
        if False:  # Disabled - desktop copy happens at end of complete workflow
            output_files = [output_file]
            if os.path.exists(summary_file):
                output_files.append(summary_file)
            
            # Add income and expense files if they exist
            income_file = os.path.join(data_dir, 'income', 'axis_income_transactions.csv')
            expense_file = os.path.join(data_dir, 'expense', 'axis_expense_transactions.csv')
            
            if os.path.exists(income_file):
                output_files.append(income_file)
            if os.path.exists(expense_file):
                output_files.append(expense_file)
            
            # Add party analysis files if they exist
            import glob
            
            # Add party analysis files with clean naming
            party_summary_file = os.path.join(data_dir, "summary", "party_wise_income_summary.txt")
            if os.path.exists(party_summary_file):
                output_files.append(party_summary_file)
            
            party_list_file = os.path.join(data_dir, "summary", "party_list_summary.txt")
            if os.path.exists(party_list_file):
                output_files.append(party_list_file)
            
            party_csv_file = os.path.join(data_dir, "income", "party", "party_list_summary.csv")
            if os.path.exists(party_csv_file):
                output_files.append(party_csv_file)
            
            party_enhanced_file = os.path.join(data_dir, "income", "party", "axis_income_with_parties.csv")
            if os.path.exists(party_enhanced_file):
                output_files.append(party_enhanced_file)
            
            desktop_dir, copied_files = processor.copy_to_desktop(output_files)
            if desktop_dir and copied_files:
                print(f"🎉 Files successfully copied to desktop: {desktop_dir}")
    else:
        print(f"❌ Consolidation failed!")

if __name__ == "__main__":
    main()
