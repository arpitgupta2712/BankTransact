#!/usr/bin/env python3
"""
Enhanced Transaction Analysis for HDFC Bank Statements
Adds intelligent categorization, subcategorization, and vendor detection

Usage: python3 enhance_transactions.py <input_csv> [output_csv]
"""

import pandas as pd
import re
import sys
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════
# VENDOR NAME EXTRACTION
# ═══════════════════════════════════════════════════════════════════════════

def extract_vendor_name(narration, transaction_type):
    """
    Extract vendor/party name from narration using common patterns
    """
    narration = str(narration).strip()
    
    # Pattern 1: NEFT CR/DR - Bank transfers
    # Format: NEFT CR-BANKCODE-VENDOR NAME-DESCRIPTION-REFNUM
    neft_match = re.search(r'NEFT (?:CR|DR)-[A-Z0-9]+-([^-]+)-', narration)
    if neft_match:
        vendor = neft_match.group(1).strip()
        # Clean up common suffixes
        vendor = re.sub(r'\s*(?:NETBANK|MUM|ONLINE)$', '', vendor, flags=re.IGNORECASE)
        return vendor
    
    # Pattern 2: IMPS transfers
    # Format: IMPS-REFNUM-VENDOR NAME-BANK-ACCOUNT-DESCRIPTION
    imps_match = re.search(r'IMPS-\d+-([^-]+)-[A-Z]{4}-', narration)
    if imps_match:
        return imps_match.group(1).strip()
    
    # Pattern 3: TPT (Third Party Transfer)
    # Format: ACCOUNT-TPT-DESCRIPTION-VENDOR NAME
    tpt_match = re.search(r'TPT-(?:[^-]*-)?(.+)$', narration)
    if tpt_match:
        return tpt_match.group(1).strip()
    
    # Pattern 4: FT (Fund Transfer)
    # Format: FT- -ACCOUNT - VENDOR NAME -
    ft_match = re.search(r'FT-\s*-\d+\s*-\s*([^-]+)\s*-', narration)
    if ft_match:
        return ft_match.group(1).strip()
    
    # Pattern 5: POS/Card transactions
    # Format: POS CARDNUM VENDOR NAME
    pos_match = re.search(r'POS\s+\d+X+\d+\s+(.+?)(?:\s+\d|$)', narration)
    if pos_match:
        vendor = pos_match.group(1).strip()
        # Clean known prefixes
        vendor = re.sub(r'^(?:PAY\*|ME DC SI|WWW\s+)', '', vendor, flags=re.IGNORECASE)
        return vendor
    
    # Pattern 6: CHQ (Cheque)
    # Format: CHQ PAID-MICR CTS-RK-VENDOR NAME
    chq_match = re.search(r'CHQ (?:PAID|DEP)-(?:MICR\s+)?(?:CTS-)?(?:RK-)?(.+)$', narration)
    if chq_match:
        return chq_match.group(1).strip()
    
    # Pattern 7: ACH (Automated Clearing House)
    # Format: ACH D- VENDOR NAME-REFNUM
    ach_match = re.search(r'ACH\s+[DC]-\s*([^-]+)-', narration)
    if ach_match:
        return ach_match.group(1).strip()
    
    # Pattern 8: CBDT (Income Tax/TDS)
    if 'CBDT' in narration:
        return 'INCOME TAX DEPARTMENT (CBDT)'
    
    # Pattern 9: Common payment methods
    if 'BFOTP' in narration or 'BAJAJ' in narration:
        return 'BAJAJ FINANCE'
    
    # Default: Return first significant part
    parts = narration.split('-')
    if len(parts) > 1:
        return parts[0].strip()
    
    return 'Unknown'

# ═══════════════════════════════════════════════════════════════════════════
# EXPENSE & INCOME CATEGORIZATION
# ═══════════════════════════════════════════════════════════════════════════

def categorize_transaction(row):
    """
    Enhanced categorization based on Goaltech patterns and Itmagia business
    Returns: (main_category, category, sub_category, vendor_name)
    """
    narration = str(row['narration']).upper()
    trans_type = str(row['transaction_type']).upper()
    trans_classification = str(row['transaction_classification']).upper()
    amount = abs(float(row['net_transaction']))
    
    # Skip inter-bank and reversed transactions
    if trans_classification in ['INTER-BANK', 'REVERSED']:
        return {
            'main_category': 'Non-Operating',
            'category': trans_classification.title(),
            'sub_category': 'Internal Transfer' if trans_classification == 'INTER-BANK' else 'Cancelled Transaction',
            'vendor_name': extract_vendor_name(narration, trans_type)
        }
    
    vendor_name = extract_vendor_name(narration, trans_type)
    
    # ═══════════════════════════════════════════════════════════════════════
    # INCOME CATEGORIZATION
    # ═══════════════════════════════════════════════════════════════════════
    
    if trans_type == 'INCOME':
        # ───────────────────────────────────────────────────────────────────
        # PRIMARY REVENUE - Core Business Income
        # ───────────────────────────────────────────────────────────────────
        
        # Paytm Settlement (Payment Gateway Fees)
        if 'ONE 97 COMMUNICATIONS' in narration or 'PAYTM' in narration:
            return {
                'main_category': 'Primary Revenue',
                'category': 'Online Booking Revenue',
                'sub_category': 'Paytm Gateway Settlement',
                'vendor_name': 'Paytm (ONE 97 COMMUNICATIONS)'
            }
        
        # Sports Venue Bookings
        if any(word in narration for word in ['TURF', 'BOOKING', 'VENUE', 'SPORTS', 'FOOTBALL']):
            if 'DECODING YOUTH' in narration:
                return {
                    'main_category': 'Primary Revenue',
                    'category': 'Venue Bookings',
                    'sub_category': 'Turf Rental - Decoding Youth Talent',
                    'vendor_name': 'DECODING YOUTH TALENT PRIVATE LIMITED'
                }
            elif 'FOOTBALL CLUB' in narration:
                return {
                    'main_category': 'Primary Revenue',
                    'category': 'Venue Bookings',
                    'sub_category': 'Monthly Venue Rental - Football Club',
                    'vendor_name': vendor_name
                }
            elif 'NAVEEN' in narration and 'TURF GRASS' in narration:
                return {
                    'main_category': 'Primary Revenue',
                    'category': 'Venue Services',
                    'sub_category': 'Turf Grass Installation Revenue',
                    'vendor_name': vendor_name
                }
            else:
                return {
                    'main_category': 'Primary Revenue',
                    'category': 'Venue Bookings',
                    'sub_category': 'Sports Venue Rental',
                    'vendor_name': vendor_name
                }
        
        # Technology/Software Services
        if any(word in narration for word in ['JOGO', 'TECHMASH', 'SOFTWARE', 'APP', 'DIGITAL']):
            return {
                'main_category': 'Secondary Revenue',
                'category': 'Technology Services',
                'sub_category': 'Software Development & Integration',
                'vendor_name': vendor_name
            }
        
        # Sports Management Services
        if 'HSQUARE SPORTS' in narration or 'VOGOV SPORTS' in narration:
            return {
                'main_category': 'Secondary Revenue',
                'category': 'Sports Management Services',
                'sub_category': 'B2B Sports Services',
                'vendor_name': vendor_name
            }
        
        # Consulting/Professional Services
        if 'SCHENCK' in narration or 'ASHRAE' in narration:
            return {
                'main_category': 'Secondary Revenue',
                'category': 'Professional Services',
                'sub_category': 'Consulting & Advisory',
                'vendor_name': vendor_name
            }
        
        # Capital/Investment (Intracompany transfers)
        if 'ITMAGIA SOLUTIONS PVT LTD' in narration and 'KKBK' in narration:
            return {
                'main_category': 'Financing Activities',
                'category': 'Internal Capital Transfer',
                'sub_category': 'Inter-Account Transfer (Own)',
                'vendor_name': 'Itmagia Solutions (Own Account)'
            }
        
        # Advance Payments from Partners
        if 'ADVANCE' in narration or 'DEPOSIT' in narration:
            return {
                'main_category': 'Primary Revenue',
                'category': 'Customer Advances',
                'sub_category': 'Advance Payment Received',
                'vendor_name': vendor_name
            }
        
        # Revenue Sharing
        if 'REVENUE SHARING' in narration:
            return {
                'main_category': 'Primary Revenue',
                'category': 'Revenue Sharing',
                'sub_category': 'Partner Revenue Share',
                'vendor_name': vendor_name
            }
        
        # Default Income
        return {
            'main_category': 'Other Income',
            'category': 'Miscellaneous Income',
            'sub_category': 'Unclassified Revenue',
            'vendor_name': vendor_name
        }
    
    # ═══════════════════════════════════════════════════════════════════════
    # EXPENSE CATEGORIZATION
    # ═══════════════════════════════════════════════════════════════════════
    
    elif trans_type == 'EXPENSE':
        # ───────────────────────────────────────────────────────────────────
        # PERSONNEL COSTS - Salaries & Bonuses
        # ───────────────────────────────────────────────────────────────────
        
        if 'SALARY' in narration:
            return {
                'main_category': 'Personnel Costs',
                'category': 'Salaries & Wages',
                'sub_category': f'Salary - {vendor_name}',
                'vendor_name': vendor_name
            }
        
        if 'BONUS' in narration:
            return {
                'main_category': 'Personnel Costs',
                'category': 'Employee Bonuses',
                'sub_category': f'Bonus - {vendor_name}',
                'vendor_name': vendor_name
            }
        
        if 'RMBRSMT' in narration or 'REIMBURSEMENT' in narration:
            return {
                'main_category': 'Personnel Costs',
                'category': 'Employee Reimbursements',
                'sub_category': f'Expense Reimbursement - {vendor_name}',
                'vendor_name': vendor_name
            }
        
        # ───────────────────────────────────────────────────────────────────
        # COST OF REVENUE - Direct Business Costs
        # ───────────────────────────────────────────────────────────────────
        
        # Turf/Venue Costs
        if any(word in narration for word in ['TURF', 'PROGREEN', 'GROW GREEN']):
            if 'PROGREEN' in narration or 'GROW GREEN' in narration:
                return {
                    'main_category': 'Cost of Revenue',
                    'category': 'Venue Infrastructure',
                    'sub_category': 'Turf Installation & Setup',
                    'vendor_name': vendor_name
                }
            elif 'TRANSPORT' in narration:
                return {
                    'main_category': 'Cost of Revenue',
                    'category': 'Logistics',
                    'sub_category': 'Turf Transportation',
                    'vendor_name': vendor_name
                }
        
        # Venue Maintenance & Supplies
        if any(word in narration for word in ['PLMB', 'PLUMBER', 'ELECTRICIAN', 'CLEANER', 'MAINTENANCE']):
            return {
                'main_category': 'Cost of Revenue',
                'category': 'Venue Maintenance',
                'sub_category': 'Repair & Maintenance Services',
                'vendor_name': vendor_name
            }
        
        # Venue Supplies & Equipment
        if any(word in narration for word in ['SANITARY', 'WATER COOLER', 'HARDWARE']):
            return {
                'main_category': 'Cost of Revenue',
                'category': 'Venue Supplies',
                'sub_category': 'Equipment & Supplies',
                'vendor_name': vendor_name
            }
        
        # ───────────────────────────────────────────────────────────────────
        # CAPITAL EXPENDITURE - Asset Purchases
        # ───────────────────────────────────────────────────────────────────
        
        if any(word in narration for word in ['TRACTOR', 'VEHICLE', 'CAR', 'BIKE']):
            return {
                'main_category': 'Capital Expenditure',
                'category': 'Vehicle & Equipment',
                'sub_category': 'Vehicle Purchase/Lease',
                'vendor_name': vendor_name
            }
        
        # ───────────────────────────────────────────────────────────────────
        # OPERATING EXPENSES - Business Operations
        # ───────────────────────────────────────────────────────────────────
        
        # Software & Technology
        if any(word in narration for word in ['GOOGLE WORKSPACE', 'SOFTWARE', 'CLOUD', 'SAAS']):
            return {
                'main_category': 'Operating Expenses',
                'category': 'Software & Technology',
                'sub_category': 'SaaS Subscriptions',
                'vendor_name': vendor_name
            }
        
        # E-commerce & Supplies
        if 'AMAZON' in narration:
            return {
                'main_category': 'Operating Expenses',
                'category': 'Office & General Supplies',
                'sub_category': 'Online Purchases (Amazon)',
                'vendor_name': 'Amazon India'
            }
        
        # Travel & Transport
        if any(word in narration for word in ['UBER', 'OLA', 'CAB', 'TAXI']):
            return {
                'main_category': 'Operating Expenses',
                'category': 'Travel & Conveyance',
                'sub_category': 'Business Travel (Cab)',
                'vendor_name': vendor_name
            }
        
        # Fuel & Vehicle Running
        if any(word in narration for word in ['PETROL', 'DIESEL', 'FUEL', 'FILLING STAT', 'HINDUSTAN PETROL']):
            return {
                'main_category': 'Operating Expenses',
                'category': 'Fuel & Vehicle Running',
                'sub_category': 'Fuel Expense',
                'vendor_name': vendor_name
            }
        
        # Professional Services
        if any(word in narration for word in ['AUDIT', 'LEGAL', 'AVK AND ASSOCIATES', 'CA ', 'ADVOCATE']):
            return {
                'main_category': 'Operating Expenses',
                'category': 'Professional Fees',
                'sub_category': 'Audit & Legal Services',
                'vendor_name': vendor_name
            }
        
        # Education/Training
        if 'SCHOOL' in narration:
            return {
                'main_category': 'Operating Expenses',
                'category': 'Education & Training',
                'sub_category': 'School/Training Fees',
                'vendor_name': vendor_name
            }
        
        # ───────────────────────────────────────────────────────────────────
        # FINANCIAL EXPENSES - Loans, Bank Charges, TDS
        # ───────────────────────────────────────────────────────────────────
        
        # Loan Repayment
        if any(word in narration for word in ['IDFC', 'BAJAJ', 'LOAN', 'EMI', 'BFOTP']):
            return {
                'main_category': 'Financing Activities',
                'category': 'Loan Repayment',
                'sub_category': 'EMI Payment',
                'vendor_name': vendor_name
            }
        
        # TDS Payment
        if 'CBDT' in narration or 'TDS' in narration:
            return {
                'main_category': 'Statutory Payments',
                'category': 'Income Tax (TDS)',
                'sub_category': 'TDS on Vendor Payments',
                'vendor_name': 'INCOME TAX DEPARTMENT (CBDT)'
            }
        
        # Bank Charges
        if any(word in narration for word in ['BANK CHARGES', 'SERVICE CHARGE', 'ATM']):
            return {
                'main_category': 'Financial Charges',
                'category': 'Bank Charges',
                'sub_category': 'Banking Service Fees',
                'vendor_name': vendor_name
            }
        
        # ACH Charges
        if 'ACH D-' in narration or 'ACH C-' in narration:
            return {
                'main_category': 'Financing Activities',
                'category': 'Loan Repayment',
                'sub_category': 'Auto Debit (ACH)',
                'vendor_name': vendor_name
            }
        
        # Default Expense
        return {
            'main_category': 'Other Expenses',
            'category': 'Miscellaneous Expenses',
            'sub_category': 'Unclassified Expense',
            'vendor_name': vendor_name
        }
    
    # ═══════════════════════════════════════════════════════════════════════
    # DEFAULT - Unknown Transaction Type
    # ═══════════════════════════════════════════════════════════════════════
    
    return {
        'main_category': 'Uncategorized',
        'category': 'Unknown',
        'sub_category': 'Needs Review',
        'vendor_name': vendor_name
    }

# ═══════════════════════════════════════════════════════════════════════════
# MAIN PROCESSING
# ═══════════════════════════════════════════════════════════════════════════

def enhance_transactions(input_file, output_file=None):
    """
    Load CSV, add categorization columns, and save enhanced version
    """
    print(f"\n{'='*70}")
    print("🔍 HDFC Transaction Enhancement & Categorization")
    print(f"{'='*70}")
    
    # Load data
    print(f"\n📂 Loading transactions from: {input_file}")
    df = pd.read_csv(input_file)
    print(f"✅ Loaded {len(df)} transactions")
    
    # Apply categorization
    print(f"\n🏷️  Analyzing and categorizing transactions...")
    categorized = df.apply(categorize_transaction, axis=1, result_type='expand')
    
    # Add new columns
    df['main_category'] = categorized['main_category']
    df['category'] = categorized['category']
    df['sub_category'] = categorized['sub_category']
    df['vendor_name'] = categorized['vendor_name']
    
    # Reorder columns for better readability
    column_order = [
        'serial_no', 'account_name', 'account_number', 'date',
        'transaction_type', 'transaction_classification',
        'main_category', 'category', 'sub_category',
        'vendor_name',
        'withdrawal_amount', 'deposit_amount', 'net_transaction',
        'narration', 'reference_number'
    ]
    
    df = df[column_order]
    
    # Generate output filename
    if output_file is None:
        input_path = Path(input_file)
        output_file = input_path.parent / f"{input_path.stem}_enhanced{input_path.suffix}"
    
    # Save enhanced file
    df.to_csv(output_file, index=False)
    print(f"\n✅ Enhanced file saved to: {output_file}")
    
    # Generate summary
    print(f"\n{'='*70}")
    print("📊 CATEGORIZATION SUMMARY")
    print(f"{'='*70}")
    
    # Income Summary
    income_df = df[df['transaction_type'] == 'Income']
    if len(income_df) > 0:
        print(f"\n💰 INCOME ANALYSIS ({len(income_df)} transactions)")
        print(f"{'─'*70}")
        income_summary = income_df.groupby(['main_category', 'category']).agg({
            'deposit_amount': 'sum',
            'serial_no': 'count'
        }).round(2)
        income_summary.columns = ['Total Amount (₹)', 'Count']
        print(income_summary.to_string())
        print(f"\n   Total Income: ₹{income_df['deposit_amount'].sum():,.2f}")
    
    # Expense Summary
    expense_df = df[df['transaction_type'] == 'Expense']
    if len(expense_df) > 0:
        print(f"\n💸 EXPENSE ANALYSIS ({len(expense_df)} transactions)")
        print(f"{'─'*70}")
        expense_summary = expense_df.groupby(['main_category', 'category']).agg({
            'withdrawal_amount': 'sum',
            'serial_no': 'count'
        }).round(2)
        expense_summary.columns = ['Total Amount (₹)', 'Count']
        print(expense_summary.to_string())
        print(f"\n   Total Expenses: ₹{expense_df['withdrawal_amount'].sum():,.2f}")
    
    # Top Vendors
    print(f"\n🏢 TOP VENDORS BY TRANSACTION VALUE")
    print(f"{'─'*70}")
    vendor_summary = df.groupby('vendor_name')['net_transaction'].agg(['sum', 'count']).abs()
    vendor_summary.columns = ['Total Value (₹)', 'Transaction Count']
    vendor_summary = vendor_summary.sort_values('Total Value (₹)', ascending=False).head(15)
    print(vendor_summary.to_string())
    
    print(f"\n{'='*70}")
    print("✨ Enhancement Complete!")
    print(f"{'='*70}\n")
    
    return output_file

# ═══════════════════════════════════════════════════════════════════════════
# COMMAND LINE INTERFACE
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 enhance_transactions.py <input_csv> [output_csv]")
        print("\nExample:")
        print("  python3 enhance_transactions.py consolidated_statements.csv")
        print("  python3 enhance_transactions.py input.csv enhanced_output.csv")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        enhance_transactions(input_file, output_file)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

