# Bank Statement Consolidator Comparison: HDFC vs AXIS

This document compares the two bank statement consolidators developed for different banks.

## Overview

Both consolidators serve the same purpose: combining multiple bank statement files into a single, cleaned, and deduplicated output with intelligent transaction classification. However, they are customized for each bank's specific statement format.

## Key Differences

| Aspect | HDFC Bank | AXIS Bank |
|--------|-----------|-----------|
| **Input Format** | Excel (.xls/.xlsx) | CSV |
| **File Structure** | Multi-sheet Excel with headers | Single CSV with embedded headers |
| **Date Format** | DD/MM/YY | DD/MM/YYYY |
| **Amount Format** | Standard (e.g., "7,560.00") | Indian numbering with tabs (e.g., "	3,932.20") |
| **Balance Format** | Standard positive/negative | Negative with commas (e.g., "-,93,43,827.31") |
| **Transaction Types** | DR/CR in separate columns | DR/CR in single column |
| **Reference Extraction** | Custom patterns for HDFC | Bank-specific patterns (NEFT, IMPS, UPI, etc.) |
| **Account Mapping** | Predefined account names | Configurable mapping |

## Technical Implementation Differences

### File Reading
- **HDFC**: Uses `pd.read_excel()` with sheet selection
- **AXIS**: Uses manual CSV parsing to handle embedded newlines and quoted fields

### Data Cleaning
- **HDFC**: Standard amount cleaning
- **AXIS**: Handles Indian numbering format and tab characters

### Balance Processing
- **HDFC**: Standard positive/negative balance handling
- **AXIS**: Special handling for "-,XX,XX,XXX.XX" format

### Reference Number Extraction
- **HDFC**: Generic patterns
- **AXIS**: Bank-specific patterns:
  - NEFT references: `NEFT/HDFCH00395034887/...`
  - IMPS references: `IMPS/P2A/423308296973/...`
  - UPI references: `UPI/P2A/423308296973/...`
  - Cheque clearing: `CLG/550691/...`
  - AXIS internal: `AXOIC23159398764`

## Sample Data Comparison

### HDFC Statement Format
```
Account No : 50200087543792
Account Branch : MUMBAI MAIN BRANCH
Statement From 01/08/2025 To 31/08/2025

Date        | Narration                    | Ref No | Value Date | Withdrawal | Deposit | Balance
01/08/2025  | NEFT CREDIT                 | ABC123 | 01/08/2025 |            | 7,560   | 1,00,000
02/08/2025  | ATM WITHDRAWAL              | XYZ789 | 02/08/2025 | 2,000      |         | 98,000
```

### AXIS Statement Format
```
Name :- BELZ INSTRUMENTS PVT LTD  .
Statement of Account No - 922030048910705 for the period (From : 01/08/2025 To : 03/08/2025)

S.No | Transaction Date | Value Date | Particulars | Amount(INR) | Debit/Credit | Balance(INR)
1    | 01/08/2025      | 01/08/2025 | NEFT/HDFCH... | "	7,560.00" | CR          | "-,77,58,122.30"
2    | 01/08/2025      | 01/08/2025 | ATM WITHDRAWAL | "	2,000.00" | DR          | "-,77,60,122.30"
```

## Output Format

Both consolidators produce the same standardized output format:

```csv
serial_no,account_name,account_number,date,value_date,narration,reference_number,transaction_type,transaction_classification,withdrawal_amount,deposit_amount,net_transaction,balance,debit_credit,cheque_number,branch_name,source_file
1,AXIS Primary,922030048910705,2024-04-02,2024-04-02,BRN-CLG-CHQ PAID TO...,BRN-CLG-CHQ PAID TO,Expense,Unique,14059.0,0.0,-14059.0,-9801446.07,DR,7742,FARIDABAD BK CH FAR HR (2568),Account_Statement_Report_19-08-2025_2313hrs (2).CSV
```

## Transaction Classification

Both consolidators use the same intelligent classification system:

1. **Unique Transactions**: External business transactions
2. **Inter-bank Transfers**: Transfers between accounts
3. **Reversed Transactions**: Failed/cancelled payments

## Performance Comparison

### HDFC Consolidator
- **Processing Speed**: Fast (Excel files are well-structured)
- **Memory Usage**: Moderate
- **File Size**: Larger (Excel format)

### AXIS Consolidator
- **Processing Speed**: Moderate (manual CSV parsing)
- **Memory Usage**: Lower
- **File Size**: Smaller (CSV format)

## Summary Statistics Comparison

### HDFC Sample Results
```
Files processed: 5
Total transactions extracted: 2,847
Period: 2024-01-01 to 2025-08-19
True business profit/loss: ₹1,234,567.89
```

### AXIS Sample Results
```
Files processed: 8
Total transactions extracted: 11,497
Period: 2024-04-02 to 2025-08-19
True business profit/loss: ₹2,117,912.22
```

## Common Features

Both consolidators share these features:

1. **Multi-file Processing**: Combines multiple statement files
2. **Intelligent Deduplication**: Identifies and handles duplicates
3. **Transaction Classification**: Categorizes transactions by type
4. **Comprehensive Summary**: Detailed financial analysis
5. **Desktop Copy**: Automatic file copying to desktop
6. **Error Handling**: Robust error handling and reporting
7. **Command Line Interface**: Flexible command line options

## Usage Patterns

### HDFC Usage
```bash
cd HDFC
python consolidate_statements.py
```

### AXIS Usage
```bash
cd AXIS
source axis_env/bin/activate  # Virtual environment required
python consolidate_statements.py
```

## Future Enhancements

Both consolidators can be extended with:

1. **Additional Bank Support**: ICICI, SBI, etc.
2. **Enhanced Analytics**: Trend analysis, forecasting
3. **Export Formats**: JSON, XML, database integration
4. **Web Interface**: GUI for easier usage
5. **Real-time Processing**: Live statement processing
6. **Multi-currency Support**: Handle different currencies

## Conclusion

Both consolidators successfully handle their respective bank's statement formats while providing the same standardized output and analysis capabilities. The main differences lie in the input format handling and data cleaning specific to each bank's statement structure.
