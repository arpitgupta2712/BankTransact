#!/usr/bin/env python3
"""
HDFC Bank Statement Consolidator
Combines multiple HDFC bank statement Excel files into a single CSV output
"""

import pandas as pd
import os
import re
import shutil
import argparse
from datetime import datetime
import numpy as np
from pathlib import Path
import json

class HDFCStatementProcessor:
    
    def __init__(self, statements_directory, config_file=None):
        self.statements_dir = statements_directory
        self.consolidated_data = []
        self.config_file = config_file or self._get_default_config_path()
        self.account_mapping = self._load_account_config()
    
    def _get_default_config_path(self):
        """Get the default path to the account config file"""
        # Try to find config file relative to this script
        script_dir = Path(__file__).parent
        config_path = script_dir / 'account_config.json'
        return str(config_path)
    
    def _load_account_config(self):
        """Load account mapping from config file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    return config.get('account_mapping', {})
            else:
                # Return default mapping if config file doesn't exist
                print(f"⚠️  Config file not found at {self.config_file}, using default mapping")
                return {
                    '50200087543792': 'Primary',
                    '99909999099865': 'Infra',
                    '99919999099866': 'Sports',
                    '99909999099867': 'B2B',
                    '99909999099868': 'B2C',
                    '99909999099869': 'Employees',
                    '50200109619138': 'Primary'
                }
        except Exception as e:
            print(f"⚠️  Error loading config file: {e}, using default mapping")
            return {
                '50200087543792': 'Primary',
                '99909999099865': 'Infra',
                '99919999099866': 'Sports',
                '99909999099867': 'B2B',
                '99909999099868': 'B2C',
                '99909999099869': 'Employees',
                '50200109619138': 'Primary'
            }
        
    def extract_account_info(self, df):
        """Extract account information from header rows"""
        account_info = {
            'account_number': None,
            'branch': None,
            'statement_period': None
        }
        
        # Extract account number from row 14, col 4
        try:
            account_text = str(df.iloc[14, 4])
            if 'Account No' in account_text:
                # Extract account number using regex
                match = re.search(r'Account No :(\d+)', account_text)
                if match:
                    account_info['account_number'] = match.group(1)
        except:
            pass
            
        # Extract branch from row 4, col 4
        try:
            branch_text = str(df.iloc[4, 4])
            if 'Account Branch' in branch_text:
                # Extract branch name
                match = re.search(r'Account Branch :(.+)', branch_text)
                if match:
                    account_info['branch'] = match.group(1).strip()
        except:
            pass
            
        # Extract statement period from row 15, col 0
        try:
            period_text = str(df.iloc[15, 0])
            if 'Statement From' in period_text:
                account_info['statement_period'] = period_text
        except:
            pass
            
        return account_info
    
    def clean_date(self, date_str):
        """Convert DD/MM/YY format to YYYY-MM-DD"""
        if pd.isna(date_str) or date_str == '':
            return None
            
        try:
            date_str = str(date_str).strip()
            # Handle DD/MM/YY format
            if '/' in date_str and len(date_str.split('/')) == 3:
                day, month, year = date_str.split('/')
                # Convert YY to YYYY (assuming 20XX for years < 50, 19XX for >= 50)
                if len(year) == 2:
                    year = '20' + year if int(year) < 50 else '19' + year
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        except:
            pass
        return None
    
    def clean_amount(self, amount_str):
        """Clean and convert amount strings to float"""
        if pd.isna(amount_str) or amount_str == '':
            return 0.0
            
        try:
            # Remove commas and convert to float
            amount_str = str(amount_str).replace(',', '').strip()
            return float(amount_str)
        except:
            return 0.0
    
    def process_single_file(self, file_path):
        """Process a single HDFC statement file"""
        print(f"Processing: {os.path.basename(file_path)}")
        
        try:
            # Read the Excel file
            df = pd.read_excel(file_path, sheet_name=0, header=None)
            
            # Extract account information
            account_info = self.extract_account_info(df)
            
            # Find transaction data start (row 22 based on our analysis)
            transaction_start_row = 22
            
            # Extract transaction data
            transactions = []
            for i in range(transaction_start_row, len(df)):
                row = df.iloc[i]
                
                # Skip empty rows or rows with all NaN
                if row.isna().all():
                    continue
                    
                # Skip rows that don't look like transactions
                date_str = str(row.iloc[0]).strip()
                if not date_str or date_str == 'nan' or len(date_str) < 5:
                    continue
                    
                # Clean the transaction data
                transaction = {
                    'account_number': account_info['account_number'],
                    'branch': account_info['branch'],
                    'date': self.clean_date(row.iloc[0]),
                    'narration': str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else '',
                    'reference_number': str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else '',
                    'value_date': self.clean_date(row.iloc[3]),
                    'withdrawal_amount': self.clean_amount(row.iloc[4]),
                    'deposit_amount': self.clean_amount(row.iloc[5]),
                    'closing_balance': self.clean_amount(row.iloc[6]),
                    'source_file': os.path.basename(file_path)
                }
                
                # Determine transaction type
                if transaction['withdrawal_amount'] > 0:
                    transaction['transaction_type'] = 'Expense'
                elif transaction['deposit_amount'] > 0:
                    transaction['transaction_type'] = 'Income'
                else:
                    transaction['transaction_type'] = 'Unknown'
                
                # Only add if we have a valid date
                if transaction['date']:
                    transactions.append(transaction)
            
            print(f"  Extracted {len(transactions)} transactions")
            return transactions
            
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
            return []
    
    def process_all_files(self):
        """Process all Excel files in the statements directory"""
        excel_files = [f for f in os.listdir(self.statements_dir) 
                      if f.endswith('.xls') or f.endswith('.xlsx')]
        
        print(f"Found {len(excel_files)} Excel files to process")
        
        all_transactions = []
        for file in excel_files:
            file_path = os.path.join(self.statements_dir, file)
            transactions = self.process_single_file(file_path)
            all_transactions.extend(transactions)
        
        return all_transactions
    
    def create_consolidated_csv(self, output_file='consolidated_bank_statements.csv'):
        """Create consolidated CSV from all bank statements"""
        print(f"\n{'='*60}")
        print("HDFC Bank Statement Consolidation")
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
        
        # Add account name mapping from config file
        df['account_name'] = df['account_number'].map(self.account_mapping).fillna('Unknown')
        
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
            Uses optimized approach to avoid exponential complexity.
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
            
            # For larger sets, use efficient approach:
            # 1. First try exact pairs and triplets (most common reversal patterns)
            # 2. Then use subset sum approach for larger groups (limited search)
            
            from itertools import combinations
            tolerance = 0.01
            
            # Check pairs first (most common case)
            for i in range(len(amounts)):
                for j in range(i + 1, len(amounts)):
                    if abs(amounts[i] + amounts[j]) < tolerance:
                        return [i, j]
            
            # Check triplets (second most common)
            if len(amounts) <= 10:  # Only for small sets to avoid performance issues
                for combo in combinations(indices, 3):
                    combo_sum = sum(amounts[i] for i in combo)
                    if abs(combo_sum) < tolerance:
                        return list(combo)
            
            # For larger sets or if no simple patterns found, use heuristic approach
            # Group by similar absolute values and check combinations within groups
            if len(amounts) > 10:
                # Create groups of transactions with similar absolute values
                amount_groups = {}
                for i, amount in enumerate(amounts):
                    abs_amount = abs(amount)
                    # Group by rounded absolute value (to nearest rupee)
                    group_key = round(abs_amount)
                    if group_key not in amount_groups:
                        amount_groups[group_key] = []
                    amount_groups[group_key].append((i, amount))
                
                # Check combinations within each group (much smaller search space)
                for group in amount_groups.values():
                    if len(group) >= 2:
                        group_indices = [item[0] for item in group]
                        group_amounts = [item[1] for item in group]
                        
                        # Check pairs within this group
                        for i in range(len(group_amounts)):
                            for j in range(i + 1, len(group_amounts)):
                                if abs(group_amounts[i] + group_amounts[j]) < tolerance:
                                    return [group_indices[i], group_indices[j]]
                        
                        # Check triplets within this group (if small enough)
                        if len(group) <= 6:
                            for combo in combinations(range(len(group)), 3):
                                combo_sum = sum(group_amounts[k] for k in combo)
                                if abs(combo_sum) < tolerance:
                                    return [group_indices[k] for k in combo]
            
            return []  # No reversal group found
        
        # Add helper columns to track reversal classification
        df['temp_classification'] = 'Unique'
        df['temp_reversal_group'] = False
        
        # Process each reference number separately
        unique_refs = df['reference_number'].unique()
        total_refs = len(unique_refs)
        print(f"🔄 Processing {total_refs} unique reference numbers for reversal detection...")
        
        for idx, ref_num in enumerate(unique_refs):
            if idx % 100 == 0 and idx > 0:  # Progress indicator every 100 refs
                print(f"   Processed {idx}/{total_refs} reference numbers ({idx/total_refs*100:.1f}%)")
            
            ref_transactions = df[df['reference_number'] == ref_num]
            
            if len(ref_transactions) == 1:
                # Single transaction - always Unique
                continue
            elif ref_transactions['account_number'].nunique() > 1:
                # Multiple accounts - check for inter-bank transfers
                if abs(ref_transactions['net_transaction'].sum()) < 0.01:
                    df.loc[df['reference_number'] == ref_num, 'temp_classification'] = 'Inter-bank'
                # else remains 'Unique' (different accounts but not clean transfer)
            else:
                # Same account, multiple transactions
                reversal_indices = find_reversal_groups(ref_transactions)
                
                if reversal_indices:
                    # Mark reversal group transactions
                    ref_indices = ref_transactions.index[reversal_indices]
                    df.loc[ref_indices, 'temp_classification'] = 'Reversed'
                    df.loc[ref_indices, 'temp_reversal_group'] = True
                
                # Remaining transactions stay as 'Unique' (like bank charges)
        
        # Apply the classification
        df['transaction_classification'] = df['temp_classification']
        
        # Clean up temporary columns
        df = df.drop(['temp_classification', 'temp_reversal_group'], axis=1)
        
        # Drop the helper columns
        df = df.drop(['net_sum', 'count', 'unique_accounts'], axis=1)
        
        # Reorder columns for better readability (added serial_no, account_name, net_transaction, and transaction_classification)
        column_order = [
            'serial_no', 'account_name', 'account_number', 'date', 'narration', 'reference_number', 
            'transaction_type', 'transaction_classification', 'withdrawal_amount', 'deposit_amount', 'net_transaction'
        ]
        df = df[column_order]
        
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
    
    def calculate_balance_changes(self, df):
        """Calculate REAL balance changes using opening and closing balances from statement summaries"""
        balance_changes = {}
        
        # Get statement summaries directly from bank statements
        excel_files = [f for f in os.listdir(self.statements_dir) 
                      if f.endswith('.xls') or f.endswith('.xlsx')]
        
        # Extract summary for each file
        for file in excel_files:
            file_path = os.path.join(self.statements_dir, file)
            summary = self.extract_statement_summary(file_path)
            
            if summary['account_number']:
                account_name = self.account_mapping.get(str(summary['account_number']), 'Unknown')
                
                if account_name != 'Unknown':
                    real_change = summary['closing_balance'] - summary['opening_balance']
                    
                    # Get transaction counts and totals from the main df
                    account_data = df[df['account_number'] == str(summary['account_number'])]
                    total_income = account_data[account_data['transaction_type'] == 'Income']['deposit_amount'].sum()
                    total_expenses = account_data[account_data['transaction_type'] == 'Expense']['withdrawal_amount'].sum()
                    
                    balance_changes[account_name] = {
                        'opening_balance': summary['opening_balance'],
                        'closing_balance': summary['closing_balance'],
                        'real_balance_change': real_change,
                        'total_income': total_income,
                        'total_expenses': total_expenses,
                        'transaction_count': len(account_data),
                        'change_direction': 'increased' if real_change > 0 else 'decreased' if real_change < 0 else 'unchanged',
                        'source_file': summary['source_file']
                    }
            
        return balance_changes
    
    def extract_statement_summary(self, file_path):
        """Extract opening and closing balances from statement summary section"""
        try:
            df = pd.read_excel(file_path, sheet_name=0, header=None)
            account_info = self.extract_account_info(df)
            
            # Look for statement summary section (usually around rows 50-70)
            opening_balance = None
            closing_balance = None
            
            # Search for "Opening Balance" in the statement summary
            for i in range(len(df)):
                try:
                    row_text = str(df.iloc[i, 0]).lower() if pd.notna(df.iloc[i, 0]) else ""
                    
                    # Look for opening balance header row
                    if "opening balance" in row_text:
                        # The values are in the next row (i+1)
                        if i + 1 < len(df):
                            values_row = df.iloc[i + 1]
                            # Opening balance is in column 0, closing balance in column 6
                            opening_balance = self.clean_amount(values_row.iloc[0])
                            if len(values_row) > 6:
                                closing_balance = self.clean_amount(values_row.iloc[6])
                            break
                                    
                except:
                    continue
            
            # If not found in summary, get from first and last transaction closing balances
            if opening_balance is None or closing_balance is None:
                transaction_start_row = 22
                first_balance = None
                last_balance = None
                
                for i in range(transaction_start_row, len(df)):
                    row = df.iloc[i]
                    if row.isna().all():
                        continue
                    
                    date_str = str(row.iloc[0]).strip()
                    if not date_str or date_str == 'nan' or len(date_str) < 5:
                        continue
                    
                    balance = self.clean_amount(row.iloc[6])
                    if balance > 0:
                        if first_balance is None:
                            first_balance = balance
                        last_balance = balance
                
                # Calculate opening balance from first transaction (closing balance - transaction amount)
                if first_balance is not None and opening_balance is None:
                    first_row = df.iloc[transaction_start_row]
                    deposit = self.clean_amount(first_row.iloc[5])
                    withdrawal = self.clean_amount(first_row.iloc[4])
                    opening_balance = first_balance - deposit + withdrawal
                
                if last_balance is not None and closing_balance is None:
                    closing_balance = last_balance
            
            return {
                'account_number': account_info['account_number'],
                'opening_balance': opening_balance or 0,
                'closing_balance': closing_balance or 0,
                'source_file': os.path.basename(file_path)
            }
            
        except Exception as e:
            print(f"Error extracting summary from {file_path}: {str(e)}")
            return {
                'account_number': None,
                'opening_balance': 0,
                'closing_balance': 0,
                'source_file': os.path.basename(file_path)
            }
    
    def generate_comprehensive_summary(self, df, output_path):
        """Generate comprehensive summary for console and file output"""
        from datetime import datetime
        
        lines = []
        lines.append("=" * 80)
        lines.append("HDFC BANK STATEMENT CONSOLIDATION - COMPREHENSIVE SUMMARY")
        lines.append("=" * 80)
        lines.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Output file: {output_path}")
        lines.append("")
        
        # Processing Summary
        lines.append("📁 PROCESSING SUMMARY")
        lines.append("-" * 40)
        excel_files = [f for f in os.listdir(self.statements_dir) 
                      if f.endswith('.xls') or f.endswith('.xlsx')]
        lines.append(f"Files processed: {len(excel_files)}")
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
        lines.append(f"{'Account':<12} | {'Txns':<5} | {'Income (₹)':<15} | {'Expenses (₹)':<15} | {'Net (₹)':<15}")
        lines.append("-" * 80)
        
        # Filter out inter-bank transactions for true business performance
        external_df = df[df['transaction_classification'] == 'Unique']
        
        total_external_income = 0
        total_external_expenses = 0
        total_external_txns = 0
        
        for account_name in ['Primary', 'Infra', 'Sports', 'B2C', 'Employees', 'B2B']:
            account_data = external_df[external_df['account_name'] == account_name]
            if len(account_data) > 0:
                acc_income = account_data[account_data['transaction_type'] == 'Income']['deposit_amount'].sum()
                acc_expenses = account_data[account_data['transaction_type'] == 'Expense']['withdrawal_amount'].sum()
                acc_net = acc_income - acc_expenses
                lines.append(f"{account_name:<12} | {len(account_data):<5} | {acc_income:<15,.2f} | {acc_expenses:<15,.2f} | {acc_net:<15,.2f}")
                
                total_external_income += acc_income
                total_external_expenses += acc_expenses
                total_external_txns += len(account_data)
        
        lines.append("-" * 80)
        lines.append(f"{'TOTAL':<12} | {total_external_txns:<5} | {total_external_income:<15,.2f} | {total_external_expenses:<15,.2f} | {total_external_income - total_external_expenses:<15,.2f}")
        lines.append("")
        
        # Account Balance Changes (REAL)
        lines.append("💹 REAL ACCOUNT BALANCE CHANGES")
        lines.append("-" * 40)
        balance_changes = self.calculate_balance_changes(df)
        total_real_change = 0
        
        lines.append(f"{'Account':<12} | {'Opening (₹)':<15} | {'Closing (₹)':<15} | {'Real Change (₹)':<15} | Status")
        lines.append("-" * 80)
        
        for account_name, change in balance_changes.items():
            status_emoji = "📈" if change['real_balance_change'] > 0 else "📉" if change['real_balance_change'] < 0 else "➡️"
            lines.append(f"{account_name:<12} | {change['opening_balance']:<15,.2f} | {change['closing_balance']:<15,.2f} | {change['real_balance_change']:<15,.2f} | {status_emoji} {change['change_direction']}")
            total_real_change += change['real_balance_change']
        
        lines.append("-" * 80)
        status_emoji = "📈" if total_real_change > 0 else "📉" if total_real_change < 0 else "➡️"
        lines.append(f"{'PORTFOLIO':<12} | {'N/A':<15} | {'N/A':<15} | {total_real_change:<15,.2f} | {status_emoji}")
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
        
        # Portfolio and business performance insights
        if len(balance_changes) > 0:
            portfolio_change = sum(change['real_balance_change'] for change in balance_changes.values())
            if portfolio_change > 0:
                lines.append(f"Total portfolio balance grew by ₹{portfolio_change:,.2f} during this period")
            elif portfolio_change < 0:
                lines.append(f"Total portfolio balance decreased by ₹{abs(portfolio_change):,.2f} during this period")
            else:
                lines.append("Total portfolio balance remained unchanged")
                
            # True business performance (external only)
            true_business_profit = external_income - external_expenses
            if true_business_profit > 0:
                lines.append(f"True business profit (external only): ₹{true_business_profit:,.2f}")
            elif true_business_profit < 0:
                lines.append(f"True business loss (external only): ₹{abs(true_business_profit):,.2f}")
            else:
                lines.append("True business performance: Break-even")
        else:
            lines.append("Unable to calculate portfolio changes")
        
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
            desktop_dir = desktop_path / f"statement_consolidated_{timestamp}"
            
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
    parser = argparse.ArgumentParser(description='HDFC Bank Statement Consolidator')
    parser.add_argument(
        '--statements-dir',
        type=str,
        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'statements'),
        help='Directory containing HDFC bank statement Excel files (default: ./data/statements)'
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
        print("Please ensure the directory exists and contains Excel files.")
        return
    
    # Check if directory has Excel files
    excel_files = [f for f in os.listdir(args.statements_dir) 
                  if f.endswith('.xls') or f.endswith('.xlsx')]
    if not excel_files:
        print(f"❌ Error: No Excel files found in: {args.statements_dir}")
        print("Please ensure the directory contains HDFC bank statement Excel files.")
        return
    
    print(f"📂 Using statements directory: {args.statements_dir}")
    print(f"📊 Found {len(excel_files)} Excel files to process")
    
    # Process statements
    processor = HDFCStatementProcessor(args.statements_dir)
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
