# Bank Transaction Processor - macOS App

A native macOS application built with SwiftUI for processing and analyzing bank statements from AXIS and HDFC banks.

## 🚀 Features

### Core Functionality
- **Multi-Bank Support**: Process statements from AXIS and HDFC banks
- **File Upload**: Drag and drop or select CSV statement files
- **Automated Processing**: Run complete workflow with single click
- **Real-time Progress**: Live status updates and debug output
- **Output Management**: View and open generated files directly from the app

### Processing Capabilities
- **Statement Consolidation**: Merge multiple statement files
- **Transaction Analysis**: Separate income and expense transactions
- **Party Analysis**: Extract and categorize party names from transactions
- **Summary Reports**: Generate comprehensive analysis reports
- **Desktop Export**: Automatically copy organized files to desktop

## 🛠 Technical Details

### Architecture
- **Framework**: SwiftUI for macOS
- **Language**: Swift 5.5+
- **Target**: macOS 15.5+
- **Architecture**: MVVM (Model-View-ViewModel)

### Key Components
- `BankTransactApp.swift`: Main app entry point
- `ContentView.swift`: Primary user interface
- `BankTransactViewModel.swift`: Business logic and data management
- `OutputViewer.swift`: File preview and management interface

### Integration
- **Python Script Integration**: Seamlessly executes existing Python workflows
- **Virtual Environment Support**: Uses bank-specific Python environments
- **File System Access**: Full read/write access to project directories
- **Process Management**: Robust async process handling with timeout protection

## 📁 Project Structure

```
BankTransactApp/
├── BankTransactApp.xcodeproj/          # Xcode project files
├── BankTransactApp/
│   ├── BankTransactApp.swift           # App entry point
│   ├── ContentView.swift               # Main UI
│   ├── BankTransactViewModel.swift     # Business logic
│   ├── OutputViewer.swift              # File viewer
│   ├── Assets.xcassets/                # App assets
│   └── BankTransactApp.entitlements    # App permissions
├── BankTransactAppTests/               # Unit tests
├── BankTransactAppUITests/             # UI tests
└── README.md                           # This file
```

## 🔧 Build & Run

### Prerequisites
- Xcode 15.0+
- macOS 15.5+
- Python 3.11+ (for backend scripts)

### Build Instructions
1. Open `BankTransactApp.xcodeproj` in Xcode
2. Select target device (macOS)
3. Build and run (⌘+R)

### Command Line Build
```bash
cd BankTransactApp
xcodebuild -project BankTransactApp.xcodeproj -scheme BankTransactApp -configuration Debug build
```

## 🎯 Usage

### Basic Workflow
1. **Select Bank**: Choose AXIS or HDFC from the bank selector
2. **Upload Files**: Click "Select Statement Files" or use existing files
3. **Process**: Click "Process Statements" to run the complete workflow
4. **View Results**: Check generated files in the output list
5. **Open Files**: Click "Open" to view files in their default application

### Advanced Features
- **Existing File Processing**: Process files already in the data directory
- **Real-time Debug**: Monitor processing progress in terminal output
- **File Management**: View all generated files with preview capabilities
- **Desktop Export**: Automatically organized output files on desktop

## 🔍 Debug & Troubleshooting

### Debug Output
The app provides comprehensive debug logging:
- Process execution status
- Python script output
- File operations
- Error messages

### Common Issues
- **Permission Errors**: Ensure app has file system access
- **Python Environment**: Verify virtual environments are properly set up
- **File Paths**: Check that bank directories exist and are accessible

## 📊 Output Files

### Generated Files
- `consolidated_[bank]_statements.csv`: Merged statement data
- `[bank]_income_transactions.csv`: Income transaction analysis
- `[bank]_income_with_parties.csv`: Income with party categorization
- `party_list_summary.csv`: Party analysis summary
- `consolidation_summary.txt`: Processing summary report
- `party_wise_income_summary.txt`: Party analysis report
- `party_list_summary.txt`: Party list summary

### File Locations
- **Project Directory**: `/BankTransact/[BANK]/data/`
- **Desktop Export**: `/Desktop/[bank]_complete_workflow_[timestamp]/`

## 🔒 Security & Permissions

### App Entitlements
- **File System Access**: Full read/write access to project directories
- **Sandbox Disabled**: For development and file system integration
- **Process Execution**: Ability to run Python scripts

### Data Privacy
- **Local Processing**: All data processed locally
- **No Network Access**: No data transmitted externally
- **Temporary Files**: Cleaned up after processing

## 🚀 Performance

### Optimization Features
- **Async Processing**: Non-blocking UI during script execution
- **Memory Management**: Efficient file handling and cleanup
- **Timeout Protection**: 5-minute timeout for script execution
- **Progress Tracking**: Real-time status updates

### Performance Metrics
- **Processing Speed**: ~5000 transactions in ~30 seconds
- **Memory Usage**: Minimal memory footprint
- **File I/O**: Optimized for large CSV files

## 🔄 Version History

### v2.0.0 (Current)
- ✅ Complete SwiftUI macOS app
- ✅ Multi-bank support (AXIS, HDFC)
- ✅ Real-time processing with debug output
- ✅ Integrated file management
- ✅ Desktop export functionality
- ✅ Party analysis integration
- ✅ Comprehensive error handling

### v1.x.x (Previous)
- Python-only implementation
- Command-line interface
- Basic consolidation features

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch
3. Make changes with proper testing
4. Submit pull request

### Code Standards
- Swift coding conventions
- MVVM architecture
- Comprehensive error handling
- Debug logging for troubleshooting

## 📄 License

This project is part of the BankTransact suite. See main repository for license details.

## 🆘 Support

For issues and questions:
1. Check debug output in terminal
2. Verify Python environment setup
3. Ensure file permissions are correct
4. Review error messages in app status

---

**Built with ❤️ using SwiftUI for macOS**
