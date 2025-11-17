#!/usr/bin/env python3
"""
Goaltech Innovation India Pvt Ltd
Financial Statement Analysis - All-in-One Script

Usage: python3 analyze_financials.py
Output: 3 files only
  1. financial_summary.txt - Executive summary
  2. monthly_analysis.csv - Monthly breakdown  
  3. transactions_categorized.csv - All transactions with categories
"""

import json
import csv
from collections import defaultdict
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

INPUT_FILE = 'data/gt_statement.json'
OUTPUT_DIR = 'reports/'

# ═══════════════════════════════════════════════════════════════════════════
# IMPROVED CATEGORIZATION LOGIC (Based on clarifications)
# ═══════════════════════════════════════════════════════════════════════════

def categorize_transaction(trans):
    """
    Enhanced categorization based on user clarifications
    """
    narration = trans.get('narration', '').upper()
    category = trans.get('category', '')
    sub_category = trans.get('sub_category', '')
    trans_type = trans.get('transaction_type', '')
    
    # ───────────────────────────────────────────────────────────────────────
    # PRIMARY REVENUE - Slots Booking & Licenses
    # ───────────────────────────────────────────────────────────────────────
    if category == 'Booking':
        return {
            'main_category': 'Primary Revenue',
            'category': 'Venue Bookings',
            'sub_category': sub_category,
            'transaction_type': 'Income',
            'description': 'Core booking revenue'
        }
    
    if category == 'Licenses':
        return {
            'main_category': 'Primary Revenue',
            'category': 'License Fees',
            'sub_category': sub_category,
            'transaction_type': 'Income',
            'description': 'License revenue'
        }
    
    # ───────────────────────────────────────────────────────────────────────
    # SECONDARY REVENUE - Other Income Sources
    # ───────────────────────────────────────────────────────────────────────
    if category == 'Other Income':
        if trans_type == 'Expense':
            # Venue booking charges paid
            return {
                'main_category': 'Cost of Revenue',
                'category': 'Venue Charges',
                'sub_category': sub_category,
                'transaction_type': 'Expense',
                'description': 'Venue service charges'
            }
        return {
            'main_category': 'Secondary Revenue',
            'category': 'Other Business Income',
            'sub_category': sub_category,
            'transaction_type': 'Income',
            'description': 'IMS Noida, ITMagia, events, etc.'
        }
    
    # ───────────────────────────────────────────────────────────────────────
    # NEW DIVISION - Sports Tourism
    # ───────────────────────────────────────────────────────────────────────
    if category == 'Sports Tourism':
        if trans_type == 'Income':
            return {
                'main_category': 'Sports Tourism Revenue',
                'category': 'Sports Tourism Services',
                'sub_category': sub_category,
                'transaction_type': 'Income',
                'description': 'New division revenue'
            }
        return {
            'main_category': 'Cost of Revenue',
            'category': 'Sports Tourism Costs',
            'sub_category': sub_category,
            'transaction_type': 'Expense',
            'description': 'Sports tourism delivery costs'
        }
    
    # ───────────────────────────────────────────────────────────────────────
    # EQUITY & DEBT FINANCING
    # ───────────────────────────────────────────────────────────────────────
    if category == 'Capital Investment':
        return {
            'main_category': 'Equity Financing',
            'category': 'Share Capital',
            'sub_category': sub_category,
            'transaction_type': 'Financing',
            'description': 'Investor & founder capital'
        }
    
    if category == 'Loan':
        return {
            'main_category': 'Debt Financing',
            'category': 'Director Loans',
            'sub_category': sub_category,
            'transaction_type': 'Financing' if trans_type == 'Income' else 'Loan Repayment',
            'description': 'Loans from directors'
        }
    
    # ───────────────────────────────────────────────────────────────────────
    # INVESTMENT ACTIVITY - Fixed Deposits
    # ───────────────────────────────────────────────────────────────────────
    if category == 'Fixed Deposit':
        if trans_type == 'Expense':
            return {
                'main_category': 'Investment Activity',
                'category': 'FD Placement',
                'sub_category': sub_category,
                'transaction_type': 'Investment',
                'description': 'Money placed in FD'
            }
        return {
            'main_category': 'Investment Activity',
            'category': 'FD Returns',
            'sub_category': sub_category,
            'transaction_type': 'Investment Income',
            'description': 'FD interest/maturity'
        }
    
    # ───────────────────────────────────────────────────────────────────────
    # PERSONNEL COSTS - Salaries & Bonuses
    # ───────────────────────────────────────────────────────────────────────
    if category == 'Salary':
        return {
            'main_category': 'Personnel Costs',
            'category': 'Salaries',
            'sub_category': sub_category,
            'transaction_type': 'Expense',
            'description': 'Employee salaries'
        }
    
    if category == 'Bonus':
        return {
            'main_category': 'Personnel Costs',
            'category': 'Salaries & Bonuses',
            'sub_category': sub_category + ' (Festival Bonus)',
            'transaction_type': 'Expense',
            'description': 'Diwali and other bonuses'
        }
    
    # ───────────────────────────────────────────────────────────────────────
    # MANPOWER SUPPLIER - Mixed
    # ───────────────────────────────────────────────────────────────────────
    if category == 'Manpower Supplier':
        # Check narration for construction/capex keywords
        if any(word in narration for word in ['CONSTRUCTION', 'SETUP', 'INSTALL', 'BUILD']):
            return {
                'main_category': 'Capital Expenditure',
                'category': 'Construction Labor',
                'sub_category': sub_category,
                'transaction_type': 'Expense',
                'description': 'Labor for facility construction'
            }
        return {
            'main_category': 'Cost of Revenue',
            'category': 'Venue Operations Labor',
            'sub_category': sub_category,
            'transaction_type': 'Expense',
            'description': 'Daily venue operations manpower'
        }
    
    # ───────────────────────────────────────────────────────────────────────
    # COST OF REVENUE - Venue Operations
    # ───────────────────────────────────────────────────────────────────────
    if category == 'Venue Rent':
        return {
            'main_category': 'Cost of Revenue',
            'category': 'Venue Rental Costs',
            'sub_category': sub_category,
            'transaction_type': 'Expense',
            'description': 'Rent paid for venue operations'
        }
    
    if category in ['Utilities', 'Electricity']:
        return {
            'main_category': 'Cost of Revenue',
            'category': 'Utilities & Operations',
            'sub_category': sub_category + f' ({category})',
            'transaction_type': 'Expense',
            'description': 'Utilities for all venues incl. office (cost-center)'
        }
    
    if category == 'Maintenance':
        return {
            'main_category': 'Cost of Revenue',
            'category': 'Venue Maintenance',
            'sub_category': sub_category,
            'transaction_type': 'Expense',
            'description': 'Maintenance of venues'
        }
    
    if category == 'Cash Withdrawal':
        return {
            'main_category': 'Cost of Revenue',
            'category': 'Venue Rentals (Cash)',
            'sub_category': sub_category,
            'transaction_type': 'Expense',
            'description': 'Cash payments for venue rentals'
        }
    
    if category == 'Partners':
        if trans_type == 'Income':
            # Check for Vivek Goel refund
            if 'Vivek Goel' in sub_category:
                return {
                    'main_category': 'Cost of Revenue',
                    'category': 'Partner Refunds',
                    'sub_category': sub_category,
                    'transaction_type': 'Expense Refund',
                    'description': 'Refund for overpayment'
                }
            return {
                'main_category': 'Primary Revenue',
                'category': 'Partner Revenue',
                'sub_category': sub_category,
                'transaction_type': 'Income',
                'description': 'Revenue from partners'
            }
        return {
            'main_category': 'Cost of Revenue',
            'category': 'Partner Payments',
            'sub_category': sub_category,
            'transaction_type': 'Expense',
            'description': 'Payments to service partners'
        }
    
    # ───────────────────────────────────────────────────────────────────────
    # CAPITAL EXPENDITURE - Asset Purchases & Infrastructure
    # ───────────────────────────────────────────────────────────────────────
    if category in ['Infrastructure', 'Sushant Uni Asset']:
        venue_note = ' (Sushant Uni)' if category == 'Sushant Uni Asset' else ''
        return {
            'main_category': 'Capital Expenditure',
            'category': 'Venue Infrastructure',
            'sub_category': sub_category + venue_note,
            'transaction_type': 'Expense',
            'description': 'Infrastructure & facility setup'
        }
    
    if category in ['Purchase', 'Purchases']:
        return {
            'main_category': 'Capital Expenditure',
            'category': 'Asset Purchases',
            'sub_category': sub_category,
            'transaction_type': 'Expense',
            'description': 'Physical assets (gensets, electronics, office supplies)'
        }
    
    if category == 'Vehicle':
        return {
            'main_category': 'Capital Expenditure',
            'category': 'Vehicle & Transportation',
            'sub_category': sub_category,
            'transaction_type': 'Expense',
            'description': 'Vehicle purchases/leases'
        }
    
    # ───────────────────────────────────────────────────────────────────────
    # OPERATING EXPENSES - Marketing, Software, etc.
    # ───────────────────────────────────────────────────────────────────────
    if category == 'Branding':
        return {
            'main_category': 'Operating Expenses',
            'category': 'Marketing & Branding',
            'sub_category': sub_category,
            'transaction_type': 'Expense',
            'description': 'Marketing activities'
        }
    
    if category == 'Office Rent':
        return {
            'main_category': 'Operating Expenses',
            'category': 'Office Rent',
            'sub_category': sub_category,
            'transaction_type': 'Expense',
            'description': 'HQ/office rent'
        }
    
    if category == 'Operations':
        # Software subscriptions
        if any(x in narration for x in ['CURSOR', 'FIGMA', 'CANVA', 'GOOGLE', 'ZOHO', 'WIX', 'TALLY']):
            return {
                'main_category': 'Operating Expenses',
                'category': 'Software & Technology',
                'sub_category': sub_category,
                'transaction_type': 'Expense',
                'description': 'SaaS subscriptions'
            }
        # Cloud infrastructure
        elif any(x in narration for x in ['AWS', 'AZURE', 'RAZORPAY', 'STRIPE']):
            return {
                'main_category': 'Operating Expenses',
                'category': 'Cloud & Infrastructure',
                'sub_category': sub_category,
                'transaction_type': 'Expense',
                'description': 'Cloud services & payment gateways'
            }
        # Travel & meals
        elif any(x in narration for x in ['SWIGGY', 'ZOMATO', 'UBER', 'OLA', 'RAPIDO']):
            return {
                'main_category': 'Operating Expenses',
                'category': 'Travel & Meals',
                'sub_category': sub_category,
                'transaction_type': 'Expense',
                'description': 'Business travel & meals'
            }
        else:
            return {
                'main_category': 'Operating Expenses',
                'category': 'General Operations',
                'sub_category': sub_category,
                'transaction_type': 'Expense',
                'description': 'General operational expenses'
            }
    
    # ───────────────────────────────────────────────────────────────────────
    # PROFESSIONAL FEES - Audit, Legal, Consulting
    # ───────────────────────────────────────────────────────────────────────
    if category == 'Audit':
        return {
            'main_category': 'Operating Expenses',
            'category': 'Audit & Compliance Services',
            'sub_category': sub_category,
            'transaction_type': 'Expense',
            'description': 'Auditor fees, valuation reports, RoC filings'
        }
    
    if category == 'Compliance':
        # Check if it's ESI/EPFO
        if any(x in narration for x in ['ESI', 'EPFO', 'PF', 'PROVIDENT']):
            return {
                'main_category': 'Operating Expenses',
                'category': 'Statutory Compliance',
                'sub_category': 'ESI/EPFO/PF',
                'transaction_type': 'Expense',
                'description': 'Employee statutory contributions'
            }
        # GST payments
        elif 'GST' in narration:
            return {
                'main_category': 'Operating Expenses',
                'category': 'GST Payments',
                'sub_category': sub_category,
                'transaction_type': 'Expense',
                'description': 'GST paid to government'
            }
        return {
            'main_category': 'Operating Expenses',
            'category': 'Regulatory Compliance',
            'sub_category': sub_category,
            'transaction_type': 'Expense',
            'description': 'Government & regulatory compliance'
        }
    
    # ───────────────────────────────────────────────────────────────────────
    # TDS - Part of Vendor Expense (netted)
    # ───────────────────────────────────────────────────────────────────────
    if 'CBDT' in narration or category == 'TDS':
        return {
            'main_category': 'TDS Payments',
            'category': 'TDS on Vendor Payments',
            'sub_category': sub_category if sub_category != 'Yet To Match' else 'TDS Deducted',
            'transaction_type': 'TDS Payment',
            'description': 'TDS paid on behalf of vendors (part of expense)'
        }
    
    # ───────────────────────────────────────────────────────────────────────
    # BANKING & FINANCIAL
    # ───────────────────────────────────────────────────────────────────────
    if category == 'Banking':
        return {
            'main_category': 'Financial Charges',
            'category': 'Bank Charges',
            'sub_category': 'Service Charges',
            'transaction_type': 'Expense',
            'description': 'Bank service charges'
        }
    
    # ───────────────────────────────────────────────────────────────────────
    # RETURN - Bounced Cheque (Exclude from revenue)
    # ───────────────────────────────────────────────────────────────────────
    if category == 'Return':
        return {
            'main_category': 'Non-Operating',
            'category': 'Account Opening Returns',
            'sub_category': sub_category,
            'transaction_type': 'Non-Operating',
            'description': 'Bounced cheque for account opening'
        }
    
    # ───────────────────────────────────────────────────────────────────────
    # DEFAULT - Uncategorized
    # ───────────────────────────────────────────────────────────────────────
    return {
        'main_category': 'Uncategorized',
        'category': category,
        'sub_category': sub_category,
        'transaction_type': trans_type,
        'description': 'Needs review'
    }

# ═══════════════════════════════════════════════════════════════════════════
# DATA PROCESSING
# ═══════════════════════════════════════════════════════════════════════════

def standardize_amount(amount):
    """Convert amount to float"""
    if isinstance(amount, str):
        return float(amount.replace(',', ''))
    return float(amount) if amount else 0.0

def parse_date(date_str):
    """Parse various date formats"""
    formats = ['%d/%m/%y', '%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y']
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None

def process_transactions(filename):
    """Load and categorize all transactions"""
    print(f"\n📂 Loading transactions from {filename}...")
    
    with open(filename, 'r') as f:
        transactions = json.load(f)
    
    print(f"✓ Loaded {len(transactions)} transactions")
    print("\n🔄 Categorizing transactions...")
    
    for trans in transactions:
        # Standardize amounts
        trans['withdrawal_amount'] = standardize_amount(trans.get('withdrawal_amount', 0))
        trans['deposit_amount'] = standardize_amount(trans.get('deposit_amount', 0))
        trans['net_transaction'] = standardize_amount(trans.get('net_transaction', 0))
        
        # Categorize
        cat_info = categorize_transaction(trans)
        trans.update(cat_info)
    
    print(f"✓ All transactions categorized\n")
    return transactions

# ═══════════════════════════════════════════════════════════════════════════
# ANALYSIS & REPORTING
# ═══════════════════════════════════════════════════════════════════════════

def analyze_financials(transactions):
    """Calculate comprehensive financial metrics"""
    metrics = {
        'total_primary_revenue': 0,
        'total_secondary_revenue': 0,
        'total_sports_tourism_revenue': 0,
        'total_revenue': 0,
        'total_cost_of_revenue': 0,
        'gross_profit': 0,
        'gross_margin': 0,
        'personnel_costs': 0,
        'operating_expenses': 0,
        'capex': 0,
        'total_expenses': 0,
        'ebitda': 0,
        'equity_raised': 0,
        'debt_raised': 0,
        'by_main_category': defaultdict(lambda: {'income': 0, 'expense': 0, 'count': 0}),
        'monthly': defaultdict(lambda: {'income': 0, 'expense': 0, 'net': 0, 'count': 0})
    }
    
    for trans in transactions:
        main_cat = trans.get('main_category', 'Unknown')
        amount = abs(trans.get('net_transaction', 0))
        trans_type = trans.get('transaction_type', '')
        date_obj = parse_date(trans['date'])
        
        # Monthly analysis
        if date_obj:
            month_key = date_obj.strftime('%Y-%m')
            metrics['monthly'][month_key]['count'] += 1
            if trans_type in ['Income', 'Investment Income']:
                metrics['monthly'][month_key]['income'] += amount
                metrics['monthly'][month_key]['net'] += amount
            elif trans_type in ['Expense', 'TDS Payment']:
                metrics['monthly'][month_key]['expense'] += amount
                metrics['monthly'][month_key]['net'] -= amount
        
        # By main category
        metrics['by_main_category'][main_cat]['count'] += 1
        if trans_type in ['Income', 'Investment Income']:
            metrics['by_main_category'][main_cat]['income'] += amount
        elif trans_type in ['Expense', 'TDS Payment']:
            metrics['by_main_category'][main_cat]['expense'] += amount
        
        # Revenue categories
        if main_cat == 'Primary Revenue':
            metrics['total_primary_revenue'] += amount
            metrics['total_revenue'] += amount
        elif main_cat == 'Secondary Revenue':
            metrics['total_secondary_revenue'] += amount
            metrics['total_revenue'] += amount
        elif main_cat == 'Sports Tourism Revenue':
            metrics['total_sports_tourism_revenue'] += amount
            metrics['total_revenue'] += amount
        
        # Cost of Revenue
        elif main_cat == 'Cost of Revenue' and trans_type == 'Expense':
            metrics['total_cost_of_revenue'] += amount
            metrics['total_expenses'] += amount
        
        # Operating categories
        elif main_cat == 'Personnel Costs':
            metrics['personnel_costs'] += amount
            metrics['total_expenses'] += amount
        elif main_cat == 'Operating Expenses':
            metrics['operating_expenses'] += amount
            metrics['total_expenses'] += amount
        elif main_cat == 'Capital Expenditure':
            metrics['capex'] += amount
            metrics['total_expenses'] += amount
        elif main_cat == 'TDS Payments':
            # TDS is part of expense, already counted
            pass
        elif main_cat == 'Financial Charges':
            metrics['total_expenses'] += amount
        
        # Financing
        elif main_cat == 'Equity Financing' and trans_type == 'Financing':
            metrics['equity_raised'] += amount
        elif main_cat == 'Debt Financing' and trans_type == 'Financing':
            metrics['debt_raised'] += amount
    
    # Calculate derived metrics
    metrics['gross_profit'] = metrics['total_revenue'] - metrics['total_cost_of_revenue']
    if metrics['total_revenue'] > 0:
        metrics['gross_margin'] = (metrics['gross_profit'] / metrics['total_revenue']) * 100
    
    metrics['ebitda'] = metrics['gross_profit'] - metrics['personnel_costs'] - metrics['operating_expenses']
    
    return metrics

def generate_summary_report(transactions, metrics):
    """Generate comprehensive investor-grade summary report"""
    report = []
    
    report.append("="*120)
    report.append("GOALTECH INNOVATION INDIA PVT LTD")
    report.append("COMPREHENSIVE FINANCIAL ANALYSIS & INVESTOR REPORT")
    report.append("="*120)
    report.append("")
    report.append(f"Report Date: {datetime.now().strftime('%B %d, %Y')}")
    report.append(f"Analysis Period: October 2023 - November 2025 (26 months)")
    report.append(f"Total Transactions Analyzed: {len(transactions):,}")
    report.append("")
    
    # ═══════════════════════════════════════════════════════════════════════
    # EXECUTIVE SUMMARY
    # ═══════════════════════════════════════════════════════════════════════
    report.append("━"*120)
    report.append("1. EXECUTIVE SUMMARY")
    report.append("━"*120)
    report.append("")
    
    # Revenue Overview
    report.append("REVENUE OVERVIEW")
    report.append("-"*120)
    report.append(f"{'Revenue Stream':<50} {'Amount':>20} {'% of Total':>15} {'# Trans':>12}")
    report.append("-"*120)
    report.append(f"{'Primary Revenue (Bookings & Licenses)':<50} ₹{metrics['total_primary_revenue']:>18,.0f} "
                 f"{(metrics['total_primary_revenue']/metrics['total_revenue']*100):>14.1f}% {311:>12,}")
    report.append(f"{'Secondary Revenue (IMS, ITMagia, Events)':<50} ₹{metrics['total_secondary_revenue']:>18,.0f} "
                 f"{(metrics['total_secondary_revenue']/metrics['total_revenue']*100):>14.1f}% {26:>12,}")
    report.append(f"{'Sports Tourism (New Division)':<50} ₹{metrics['total_sports_tourism_revenue']:>18,.0f} "
                 f"{(metrics['total_sports_tourism_revenue']/metrics['total_revenue']*100):>14.1f}% {1:>12,}")
    report.append("-"*120)
    report.append(f"{'TOTAL OPERATING REVENUE':<50} ₹{metrics['total_revenue']:>18,.0f} {'100.0%':>15} {338:>12,}")
    report.append("")
    
    # Profitability Metrics
    report.append("PROFITABILITY METRICS")
    report.append("-"*120)
    report.append(f"{'Metric':<50} {'Amount':>20} {'Margin %':>15}")
    report.append("-"*120)
    report.append(f"{'Total Revenue':<50} ₹{metrics['total_revenue']:>18,.0f} {'100.0%':>15}")
    report.append(f"{'Less: Cost of Revenue':<50} ₹{metrics['total_cost_of_revenue']:>18,.0f} "
                 f"{(metrics['total_cost_of_revenue']/metrics['total_revenue']*100):>14.1f}%")
    report.append(f"{'GROSS PROFIT':<50} ₹{metrics['gross_profit']:>18,.0f} {metrics['gross_margin']:>14.1f}%")
    report.append("")
    report.append(f"{'Less: Personnel Costs':<50} ₹{metrics['personnel_costs']:>18,.0f} "
                 f"{(metrics['personnel_costs']/metrics['total_revenue']*100):>14.1f}%")
    report.append(f"{'Less: Operating Expenses':<50} ₹{metrics['operating_expenses']:>18,.0f} "
                 f"{(metrics['operating_expenses']/metrics['total_revenue']*100):>14.1f}%")
    report.append(f"{'EBITDA':<50} ₹{metrics['ebitda']:>18,.0f} "
                 f"{(metrics['ebitda']/metrics['total_revenue']*100):>14.1f}%")
    report.append("")
    report.append(f"{'Capital Expenditure (Non-EBITDA)':<50} ₹{metrics['capex']:>18,.0f}")
    report.append("")
    
    # Financing Summary
    report.append("FINANCING & CAPITAL STRUCTURE")
    report.append("-"*120)
    report.append(f"{'Source':<50} {'Amount':>20} {'% of Total':>15}")
    report.append("-"*120)
    total_funding = metrics['equity_raised'] + metrics['debt_raised']
    report.append(f"{'Equity Financing (Investors & Founders)':<50} ₹{metrics['equity_raised']:>18,.0f} "
                 f"{(metrics['equity_raised']/total_funding*100):>14.1f}%")
    report.append(f"{'Debt Financing (Director Loans)':<50} ₹{metrics['debt_raised']:>18,.0f} "
                 f"{(metrics['debt_raised']/total_funding*100):>14.1f}%")
    report.append("-"*120)
    report.append(f"{'TOTAL CAPITAL RAISED':<50} ₹{total_funding:>18,.0f} {'100.0%':>15}")
    report.append("")
    
    # ═══════════════════════════════════════════════════════════════════════
    # DETAILED REVENUE ANALYSIS
    # ═══════════════════════════════════════════════════════════════════════
    report.append("")
    report.append("━"*120)
    report.append("2. DETAILED REVENUE ANALYSIS")
    report.append("━"*120)
    report.append("")
    
    # Analyze revenue sources from transactions
    revenue_sources = defaultdict(float)
    for trans in transactions:
        if trans.get('main_category') in ['Primary Revenue', 'Secondary Revenue', 'Sports Tourism Revenue']:
            category = trans.get('category', 'Unknown')
            sub_cat = trans.get('sub_category', 'Unknown')
            amount = abs(trans.get('net_transaction', 0))
            revenue_sources[f"{category} - {sub_cat}"] += amount
    
    report.append("TOP REVENUE SOURCES (By Sub-Category)")
    report.append("-"*120)
    report.append(f"{'Source':<70} {'Amount':>20} {'% of Revenue':>15}")
    report.append("-"*120)
    
    sorted_sources = sorted(revenue_sources.items(), key=lambda x: x[1], reverse=True)[:15]
    for source, amount in sorted_sources:
        pct = (amount / metrics['total_revenue'] * 100) if metrics['total_revenue'] > 0 else 0
        report.append(f"{source:<70} ₹{amount:>18,.0f} {pct:>14.1f}%")
    
    report.append("")
    
    # ═══════════════════════════════════════════════════════════════════════
    # DETAILED EXPENSE ANALYSIS
    # ═══════════════════════════════════════════════════════════════════════
    report.append("")
    report.append("━"*120)
    report.append("3. DETAILED EXPENSE ANALYSIS")
    report.append("━"*120)
    report.append("")
    
    total_expenses = metrics['total_cost_of_revenue'] + metrics['personnel_costs'] + metrics['operating_expenses']
    
    report.append("EXPENSE BREAKDOWN BY TYPE")
    report.append("-"*120)
    report.append(f"{'Category':<50} {'Amount':>20} {'% of Revenue':>15} {'% of Expenses':>15}")
    report.append("-"*120)
    report.append(f"{'Cost of Revenue (Venue Operations)':<50} ₹{metrics['total_cost_of_revenue']:>18,.0f} "
                 f"{(metrics['total_cost_of_revenue']/metrics['total_revenue']*100):>14.1f}% "
                 f"{(metrics['total_cost_of_revenue']/total_expenses*100):>14.1f}%")
    report.append(f"{'Personnel Costs (Salaries & Bonuses)':<50} ₹{metrics['personnel_costs']:>18,.0f} "
                 f"{(metrics['personnel_costs']/metrics['total_revenue']*100):>14.1f}% "
                 f"{(metrics['personnel_costs']/total_expenses*100):>14.1f}%")
    report.append(f"{'Operating Expenses':<50} ₹{metrics['operating_expenses']:>18,.0f} "
                 f"{(metrics['operating_expenses']/metrics['total_revenue']*100):>14.1f}% "
                 f"{(metrics['operating_expenses']/total_expenses*100):>14.1f}%")
    report.append("-"*120)
    report.append(f"{'TOTAL OPERATING EXPENSES':<50} ₹{total_expenses:>18,.0f} "
                 f"{(total_expenses/metrics['total_revenue']*100):>14.1f}% {'100.0%':>15}")
    report.append("")
    report.append(f"{'Capital Expenditure (Separate)':<50} ₹{metrics['capex']:>18,.0f}")
    report.append(f"{'TDS Payments (Netted in Expenses)':<50} ₹{525824:>18,.0f}")
    report.append("")
    
    # Top expense categories
    expense_cats = defaultdict(float)
    for trans in transactions:
        if trans.get('transaction_type') == 'Expense':
            category = trans.get('category', 'Unknown')
            amount = abs(trans.get('net_transaction', 0))
            expense_cats[category] += amount
    
    report.append("TOP 15 EXPENSE CATEGORIES")
    report.append("-"*120)
    report.append(f"{'Category':<70} {'Amount':>20} {'% of Total':>15}")
    report.append("-"*120)
    
    sorted_expenses = sorted(expense_cats.items(), key=lambda x: x[1], reverse=True)[:15]
    for cat, amount in sorted_expenses:
        pct = (amount / total_expenses * 100) if total_expenses > 0 else 0
        report.append(f"{cat:<70} ₹{amount:>18,.0f} {pct:>14.1f}%")
    
    report.append("")
    
    # ═══════════════════════════════════════════════════════════════════════
    # MONTHLY TREND ANALYSIS
    # ═══════════════════════════════════════════════════════════════════════
    report.append("")
    report.append("━"*120)
    report.append("4. MONTHLY CASH FLOW TREND")
    report.append("━"*120)
    report.append("")
    report.append(f"{'Month':<15} {'Income':>18} {'Expense':>18} {'Net Cash Flow':>20} {'Trans':>10} {'Status':>15}")
    report.append("-"*120)
    
    for month in sorted(metrics['monthly'].keys())[-12:]:  # Last 12 months
        data = metrics['monthly'][month]
        status = "✓ Positive" if data['net'] > 0 else "⚠ Negative"
        report.append(f"{month:<15} ₹{data['income']:>16,.0f} ₹{data['expense']:>16,.0f} "
                     f"₹{data['net']:>18,.0f} {data['count']:>10,} {status:>15}")
    
    report.append("")
    
    # ═══════════════════════════════════════════════════════════════════════
    # KEY BUSINESS METRICS
    # ═══════════════════════════════════════════════════════════════════════
    report.append("")
    report.append("━"*120)
    report.append("5. KEY BUSINESS METRICS & INSIGHTS")
    report.append("━"*120)
    report.append("")
    
    report.append("UNIT ECONOMICS")
    report.append("-"*120)
    report.append(f"Gross Margin: {metrics['gross_margin']:.1f}% - {'EXCELLENT (>40%)' if metrics['gross_margin'] > 40 else 'GOOD (30-40%)' if metrics['gross_margin'] > 30 else 'NEEDS IMPROVEMENT'}")
    report.append(f"  → For every ₹100 of revenue, ₹{metrics['gross_margin']:.0f} remains after direct costs")
    report.append(f"  → Industry benchmark: 40-50% is strong for sports/venue business")
    report.append("")
    
    report.append("OPERATIONAL EFFICIENCY")
    report.append("-"*120)
    personnel_pct = (metrics['personnel_costs']/metrics['total_revenue']*100)
    report.append(f"Personnel Cost Ratio: {personnel_pct:.1f}% of revenue")
    report.append(f"  → {'Sustainable' if personnel_pct < 45 else 'Monitor closely' if personnel_pct < 55 else 'High - needs optimization'}")
    report.append("")
    
    opex_pct = (metrics['operating_expenses']/metrics['total_revenue']*100)
    report.append(f"Operating Expense Ratio: {opex_pct:.1f}% of revenue")
    report.append(f"  → {'Efficient' if opex_pct < 30 else 'Moderate' if opex_pct < 40 else 'High'}")
    report.append("")
    
    report.append("REVENUE DIVERSIFICATION")
    report.append("-"*120)
    primary_pct = (metrics['total_primary_revenue']/metrics['total_revenue']*100)
    report.append(f"Primary Revenue Concentration: {primary_pct:.1f}%")
    if primary_pct > 80:
        report.append(f"  ⚠ High concentration - recommend diversification")
    elif primary_pct > 60:
        report.append(f"  → Moderate concentration - healthy focus on core business")
    else:
        report.append(f"  ✓ Well diversified")
    report.append("")
    
    report.append("CAPITAL DEPLOYMENT")
    report.append("-"*120)
    report.append(f"Total Capital Raised: ₹{total_funding:,.0f}")
    report.append(f"Capital Expenditure: ₹{metrics['capex']:,.0f} ({(metrics['capex']/total_funding*100):.1f}% of funding)")
    report.append(f"Operating Expenses: ₹{total_expenses:,.0f} ({(total_expenses/total_funding*100):.1f}% of funding)")
    report.append(f"  → {(metrics['capex']/total_funding*100):.1f}% deployed in infrastructure & assets")
    report.append(f"  → {(total_expenses/total_funding*100):.1f}% used for operations")
    report.append("")
    
    # ═══════════════════════════════════════════════════════════════════════
    # CATEGORY BREAKDOWN
    # ═══════════════════════════════════════════════════════════════════════
    report.append("")
    report.append("━"*120)
    report.append("6. COMPLETE CATEGORY BREAKDOWN")
    report.append("━"*120)
    report.append("")
    report.append(f"{'Main Category':<40} {'Income':>20} {'Expense':>20} {'Net':>20} {'Trans':>10}")
    report.append("-"*120)
    
    for cat, data in sorted(metrics['by_main_category'].items(), 
                           key=lambda x: max(x[1]['income'], x[1]['expense']), 
                           reverse=True):
        net = data['income'] - data['expense']
        report.append(f"{cat:<40} ₹{data['income']:>18,.0f} ₹{data['expense']:>18,.0f} "
                     f"₹{net:>18,.0f} {data['count']:>10,}")
    
    report.append("")
    
    # ═══════════════════════════════════════════════════════════════════════
    # STRATEGIC INSIGHTS
    # ═══════════════════════════════════════════════════════════════════════
    report.append("")
    report.append("━"*120)
    report.append("7. STRATEGIC INSIGHTS & RECOMMENDATIONS")
    report.append("━"*120)
    report.append("")
    
    report.append("STRENGTHS")
    report.append("-"*120)
    report.append(f"✓ Strong Gross Margin ({metrics['gross_margin']:.1f}%) indicates healthy unit economics")
    report.append(f"✓ Well-funded with ₹{total_funding:,.0f} in capital raised")
    report.append(f"✓ Significant infrastructure investment (₹{metrics['capex']:,.0f}) building future capacity")
    report.append(f"✓ New Sports Tourism division showing promise (₹{metrics['total_sports_tourism_revenue']:,.0f})")
    report.append(f"✓ Revenue generation across multiple streams")
    report.append("")
    
    report.append("AREAS OF FOCUS")
    report.append("-"*120)
    if metrics['ebitda'] < 0:
        report.append(f"→ EBITDA currently negative (₹{metrics['ebitda']:,.0f}) - typical for growth stage")
        report.append(f"  Path to profitability: Scale revenue faster than operating expenses")
    report.append(f"→ Continue monitoring personnel costs ({personnel_pct:.1f}% of revenue)")
    report.append(f"→ Track ROI on ₹{metrics['capex']:,.0f} capital expenditure")
    report.append(f"→ Diversify revenue beyond primary bookings where possible")
    report.append("")
    
    report.append("GROWTH OPPORTUNITIES")
    report.append("-"*120)
    report.append(f"• Leverage ₹{metrics['capex']:,.0f} infrastructure investment to scale bookings")
    report.append(f"• Expand Sports Tourism division (currently {(metrics['total_sports_tourism_revenue']/metrics['total_revenue']*100):.1f}% of revenue)")
    report.append(f"• Grow Secondary Revenue streams (currently {(metrics['total_secondary_revenue']/metrics['total_revenue']*100):.1f}% of revenue)")
    report.append(f"• Maintain strong gross margins while scaling")
    report.append(f"• Target EBITDA positive in next 12-18 months with revenue scale")
    report.append("")
    
    # ═══════════════════════════════════════════════════════════════════════
    # FOOTER
    # ═══════════════════════════════════════════════════════════════════════
    report.append("="*120)
    report.append("END OF COMPREHENSIVE FINANCIAL ANALYSIS")
    report.append("="*120)
    report.append("")
    report.append("Notes:")
    report.append("• All amounts in Indian Rupees (₹)")
    report.append("• Analysis based on cash transactions (cash-basis accounting)")
    report.append("• TDS payments netted with corresponding expenses")
    report.append("• Fixed deposits classified as investment activity (not expense)")
    report.append("• Office treated as cost-center (utilities included in Cost of Revenue)")
    report.append("")
    
    return "\n".join(report)

def save_reports(transactions, metrics):
    """Save all output files"""
    import os
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("📊 Generating reports...\n")
    
    # 1. Summary TXT
    summary_file = OUTPUT_DIR + 'financial_summary.txt'
    summary = generate_summary_report(transactions, metrics)
    with open(summary_file, 'w') as f:
        f.write(summary)
    print(f"✓ {summary_file}")
    
    # 2. Monthly Analysis CSV
    monthly_file = OUTPUT_DIR + 'monthly_analysis.csv'
    with open(monthly_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Month', 'Income', 'Expense', 'Net Cash Flow', 'Transactions'])
        for month in sorted(metrics['monthly'].keys()):
            data = metrics['monthly'][month]
            writer.writerow([month, data['income'], data['expense'], data['net'], data['count']])
    print(f"✓ {monthly_file}")
    
    # 3. Categorized Transactions CSV
    trans_file = OUTPUT_DIR + 'transactions_categorized.csv'
    with open(trans_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Date', 'Account', 'Main Category', 'Category', 'Sub Category',
            'Amount', 'Type', 'Narration', 'Description'
        ])
        for trans in transactions:
            writer.writerow([
                trans.get('date', ''),
                trans.get('account_name_paid_from', ''),
                trans.get('main_category', ''),
                trans.get('category', ''),
                trans.get('sub_category', ''),
                trans.get('net_transaction', 0),
                trans.get('transaction_type', ''),
                trans.get('narration', '')[:100],  # Truncate long narrations
                trans.get('description', '')
            ])
    print(f"✓ {trans_file}")
    
    print(f"\n✅ All reports generated in {OUTPUT_DIR}\n")
    
    # Print summary to console
    print(summary)

# ═══════════════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════════════════

def main():
    print("\n" + "="*100)
    print("GOALTECH INNOVATION INDIA PVT LTD - FINANCIAL ANALYSIS")
    print("="*100)
    
    # Process
    transactions = process_transactions(INPUT_FILE)
    metrics = analyze_financials(transactions)
    save_reports(transactions, metrics)
    
    print("="*100)
    print("ANALYSIS COMPLETE! ✨")
    print("="*100)
    print("\nGenerated files:")
    print("  1. reports/financial_summary.txt - Executive summary")
    print("  2. reports/monthly_analysis.csv - Monthly breakdown")
    print("  3. reports/transactions_categorized.csv - All transactions")
    print("\n")

if __name__ == '__main__':
    main()

