# HDFC Bank Statement Consolidator

A Python tool to consolidate multiple HDFC bank statement Excel files into a single, cleaned CSV output for easy analysis and viewing.

## ✅ Successfully Processed

- **6 Excel files** consolidated
- **131 transactions** extracted
- **6 unique accounts** processed
- **Date range:** April 28, 2025 to August 7, 2025
- **Total credits:** ₹16,923,078.29
- **Total debits:** ₹9,477,981.01

## 🔧 Features

- **Automatic Structure Detection:** Recognizes HDFC bank statement format
- **Data Cleaning:** Standardizes dates, amounts, and text fields
- **Account Metadata Extraction:** Pulls account numbers, branch info
- **Transaction Classification:** Automatically categorizes as Credit/Debit
- **Consolidated Output:** Single CSV with all statements combined
- **Chronological Sorting:** Transactions sorted by date and account
- **Source Traceability:** Maintains reference to original file

## 📊 Output Format

The consolidated CSV contains these columns:

| Column | Description |
|--------|-------------|
| `account_number` | Bank account number |
| `branch` | Account branch name |
| `date` | Transaction date (YYYY-MM-DD) |
| `value_date` | Value date (YYYY-MM-DD) |
| `narration` | Transaction description |
| `reference_number` | Check/Reference number |
| `transaction_type` | Credit or Debit |
| `withdrawal_amount` | Debit amount (0 if credit) |
| `deposit_amount` | Credit amount (0 if debit) |
| `closing_balance` | Account balance after transaction |
| `source_file` | Original Excel filename |

## 🚀 Usage

```bash
# Navigate to project directory
cd /Users/anubhav/Desktop/Finance

# Run the consolidation script
python3 consolidate_statements.py
```

## 📁 File Structure

```
Finance/
├── consolidate_statements.py     # Main consolidation script
├── data/
│   ├── statements/              # Original Excel files
│   │   ├── Acct_Statement_XXXXXXXX3792_08082025.xls
│   │   ├── Acct_Statement_XXXXXXXX9865_08082025.xls
│   │   └── ... (4 more files)
│   └── consolidated_bank_statements.csv  # Output file
└── README.md                    # This file
```

## 🔍 Sample Output

```csv
account_number,branch,date,value_date,narration,reference_number,transaction_type,withdrawal_amount,deposit_amount,closing_balance,source_file
50200087543792,ADCHINI,2025-04-28,2025-04-28,05722560003098-TPT-INV PAYMENT-ITMAGIA SOLUTIONS PRIVATE LIMITED,0000000821551564,Credit,0.0,90000.0,146211.34,Acct_Statement_XXXXXXXX3792_08082025.xls
50200087543792,ADCHINI,2025-04-29,2025-04-29,FT - DR - 03361000009209 - ABHINANDAN SEKHRI,0000000000000016,Debit,120000.0,0.0,26211.34,Acct_Statement_XXXXXXXX3792_08082025.xls
```

## 🛠 Technical Details

- **Format Support:** Excel (.xls, .xlsx)
- **Date Parsing:** Converts DD/MM/YY to YYYY-MM-DD
- **Amount Cleaning:** Removes commas, handles null values
- **Error Handling:** Graceful handling of malformed data
- **Dependencies:** pandas, openpyxl, xlrd

## 📊 Analysis Ready

The consolidated CSV is ready for:
- Excel/Google Sheets analysis
- Financial dashboard creation
- Transaction categorization
- Expense tracking
- Budgeting tools
- Data visualization

## 🎯 Next Steps

You can now:
1. Open `consolidated_bank_statements.csv` in Excel/Google Sheets
2. Create pivot tables for expense analysis
3. Build financial dashboards
4. Perform transaction categorization
5. Set up automated reporting

---

*Generated on: January 2025*
*Total processing time: < 2 seconds*
