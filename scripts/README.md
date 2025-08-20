# BankTransactApp Scripts

This directory contains scripts for building and running the BankTransactApp.

## Scripts

### `build_and_run.sh` (Recommended)
**Main script for building and running the app**

```bash
./scripts/build_and_run.sh
```

This script:
- ✅ Checks prerequisites (Xcode, Python)
- 🔨 Builds the SwiftUI macOS app
- 🚀 Opens the app automatically
- 📋 Shows usage instructions

### `build_app.sh`
**Legacy build script**

```bash
./scripts/build_app.sh
```

### `run_app.sh`
**Legacy run script**

```bash
./scripts/run_app.sh
```

## Quick Start

1. **From the BankTransact root directory:**
   ```bash
   ./scripts/build_and_run.sh
   ```

2. **The app will open automatically** and you can start using it!

## Requirements

- macOS with Xcode installed
- Python 3 installed
- BankTransactApp Xcode project in the `BankTransactApp/` directory

## Troubleshooting

If the build fails:
1. Make sure Xcode is installed and up to date
2. Check that all Swift files are in the correct location
3. Try cleaning the build folder in Xcode (Product → Clean Build Folder)
4. Run the script again
