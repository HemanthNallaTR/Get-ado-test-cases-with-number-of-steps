# Azure DevOps Test Case Extraction - Command Line Options

## Summary of New Features

The script now supports flexible suite selection through command-line arguments:

### ✅ **New Command-Line Options**

1. **`--suites [IDs]`** - Extract specific suite IDs
2. **`--range START END`** - Extract a range of suite IDs
3. **`--json-dir DIR`** - Custom JSON output directory
4. **`--excel-dir DIR`** - Custom Excel output directory

### 🚀 **Usage Examples**

```powershell
# Extract all suites (default behavior)
python extract_test_cases.py

# Extract only one suite
python extract_test_cases.py --suites 1410044

# Extract multiple specific suites
python extract_test_cases.py --suites 1410044 1410045 1410050

# Extract a range of suites
python extract_test_cases.py --range 1410044 1410048

# Use custom output directories
python extract_test_cases.py --suites 1410044 --json-dir my_json --excel-dir my_excel

# Get help
python extract_test_cases.py --help
```

### 📊 **What Changed**

**Before:**

- Fixed range: 1410044 to 1410100 (57 suites)
- Fixed output directories: "extracted_test_cases"

**After:**

- ✅ Flexible suite selection (specific IDs or ranges)
- ✅ Custom output directories
- ✅ Separate JSON and Excel folders
- ✅ Better error handling for invalid ranges
- ✅ Helpful command-line help

### 🔧 **Technical Details**

- Added `argparse` for command-line argument parsing
- Mutual exclusion between `--suites` and `--range` options
- Default behavior maintained for backward compatibility
- Enhanced error messages for invalid input
- Smart display of suite lists (shows full list if ≤10 suites, summary if >10)

### 💡 **Benefits**

1. **Faster Testing**: Extract just 1-2 suites for testing
2. **Selective Processing**: Skip problematic suites
3. **Custom Organization**: Use your own folder structure
4. **Better Performance**: Process fewer suites when needed
5. **Flexible Workflows**: Integrate with scripts and automation

### 🎯 **Common Use Cases**

```powershell
# Quick test with one suite
python extract_test_cases.py --suites 1410044

# Test a small range
python extract_test_cases.py --range 1410044 1410046

# Process specific problematic suites
python extract_test_cases.py --suites 1410055 1410067 1410089

# Full extraction (unchanged)
python extract_test_cases.py
```

The script now provides maximum flexibility while maintaining the same reliable extraction functionality!
