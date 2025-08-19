# AXIS Bank Statement Consolidator

This tool consolidates multiple AXIS bank statement CSV files into a single, cleaned, and deduplicated CSV output with intelligent transaction classification.

## Features

- **Multi-file Processing**: Combines multiple AXIS bank statement CSV files
- **Intelligent Deduplication**: Identifies and handles duplicate transactions
- **Transaction Classification**: 
  - **Unique**: External business transactions
  - **Inter-bank**: Transfers between accounts
  - **Reversed**: Failed/cancelled payments
- **Comprehensive Summary**: Detailed financial analysis and insights
- **Data Cleaning**: Handles AXIS-specific formatting (Indian numbering, negative balances)
- **Reference Number Extraction**: Automatically extracts transaction references

## Requirements

- Python 3.7+
- pandas >= 1.5.0
- numpy >= 1.21.0

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage
```bash
python consolidate_statements.py
```

### Custom Directory
```bash
python consolidate_statements.py --statements-dir /path/to/your/statements
```

### Skip Desktop Copy
```bash
python consolidate_statements.py --no-desktop-copy
```

## Input Format

The tool expects AXIS bank statement CSV files with the following structure:

```
Name :- BELZ INSTRUMENTS PVT LTD  .
"Joint Holder :-- "
...
Statement of Account No - 922030048910705 for the period (From : 01/08/2025 To : 03/08/2025)
S.No,Transaction Date (dd/mm/yyyy),Value Date (dd/mm/yyyy),Particulars,Amount(INR),Debit/Credit,Balance(INR),Cheque Number,Branch Name(SOL)
1,,,OPENING BALANCE,,,"-,77,65,682.30",,FARIDABAD BK CH FAR HR
2,01/08/2025,01/08/2025,NEFT/HDFCH00395034887/MARUTI SUZUKI INDIA LTD/HDFC BANK/0001173122,"	7,560.00",CR,"-,77,58,122.30",,"FARIDABAD BK CH FAR HR (248) "
...
```

## Output

The tool generates:

1. **Consolidated CSV**: `consolidated_axis_statements.csv`
   - All transactions from all files
   - Cleaned and standardized format
   - Transaction classification
   - Reference numbers extracted

2. **Summary Report**: `consolidation_summary.txt`
   - Processing statistics
   - Financial summaries
   - Transaction type breakdowns
   - Key insights

3. **Desktop Copy**: Files copied to timestamped directory on desktop

## Output Columns

- `serial_no`: Sequential transaction number
- `account_name`: Account identifier
- `account_number`: Bank account number
- `date`: Transaction date (YYYY-MM-DD)
- `value_date`: Value date (YYYY-MM-DD)
- `narration`: Transaction description
- `reference_number`: Extracted reference number
- `transaction_type`: Income/Expense/Unknown
- `transaction_classification`: Unique/Inter-bank/Reversed
- `withdrawal_amount`: Debit amount
- `deposit_amount`: Credit amount
- `net_transaction`: Net amount (deposit - withdrawal)
- `balance`: Running balance
- `debit_credit`: DR/CR indicator
- `cheque_number`: Cheque number (if applicable)
- `branch_name`: Branch name
- `source_file`: Original file name

## Transaction Classification Logic

### Unique Transactions
- Single transactions with no matching reversals
- External business transactions

### Inter-bank Transfers
- Multiple transactions with same reference number across different accounts
- Net sum approximately zero

### Reversed Transactions
- Pairs or groups of transactions that cancel each other out
- Failed or cancelled payments

## Key Features

### Data Cleaning
- Handles Indian numbering format (commas in amounts)
- Converts DD/MM/YYYY dates to YYYY-MM-DD
- Cleans negative balance format ("-,93,43,827.31")

### Reference Number Extraction
- NEFT references: `NEFT/HDFCH00395034887/...`
- IMPS references: `IMPS/P2A/423308296973/...`
- UPI references: `UPI/P2A/423308296973/...`
- Cheque clearing: `CLG/550691/...`
- AXIS internal: `AXOIC23159398764`

### Financial Analysis
- True business performance (external transactions only)
- Account-wise summaries
- Transaction volume analysis
- Balance change tracking

## Example Output Summary

```
================================================================================
AXIS BANK STATEMENT CONSOLIDATION - COMPREHENSIVE SUMMARY
================================================================================
Generated on: 2025-01-27 15:30:45
Output file: /path/to/consolidated_axis_statements.csv

📁 PROCESSING SUMMARY
----------------------------------------
Files processed: 8
Total transactions extracted: 12,847

📅 DATE RANGE ANALYSIS
----------------------------------------
Period: 2024-08-20 to 2025-08-19
Duration: 364 days (12.0 months)

🏦 ACCOUNT SUMMARY
----------------------------------------
Total unique accounts: 1
  AXIS Primary (922030048910705): 12,847 transactions

💰 TRANSACTION TYPE BREAKDOWN
----------------------------------------
Total Income transactions: 6,423 (₹45,67,89,123.45)
Total Expense transactions: 6,424 (₹44,32,10,987.65)
External Income transactions: 5,890 (₹42,15,67,890.12)
External Expense transactions: 5,891 (₹41,23,45,678.90)
True business profit/loss: ₹92,22,211.22

🔄 TRANSACTION CLASSIFICATION
----------------------------------------
Unique transactions: 11,781 (external business transactions)
Inter-bank transfers: 533 (transfers between accounts)
Reversed transactions: 533 (failed/cancelled payments)
```

## Troubleshooting

### Common Issues

1. **No CSV files found**: Ensure files have `.CSV` or `.csv` extension
2. **Header not found**: Check if CSV files follow AXIS format
3. **Date parsing errors**: Verify date format is DD/MM/YYYY
4. **Amount parsing errors**: Check for proper Indian numbering format

### File Structure Requirements

- Files must be in CSV format
- Must contain standard AXIS bank statement headers
- Transaction data must start after the header row
- Dates must be in DD/MM/YYYY format

## Comparison with HDFC Consolidator

| Feature | HDFC | AXIS |
|---------|------|------|
| Input Format | Excel (.xls/.xlsx) | CSV |
| Date Format | DD/MM/YY | DD/MM/YYYY |
| Amount Format | Standard | Indian numbering |
| Balance Format | Standard | Negative with commas |
| Reference Extraction | Custom patterns | Bank-specific patterns |
| Account Mapping | Predefined | Configurable |

## License

This tool is provided as-is for educational and business use.
