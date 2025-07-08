# Azure DevOps Test Case Extraction Script

This script extracts test case data from Azure DevOps and saves them in both JSON and Excel formats in separate folders.

## Features

- Extracts test cases from Azure DevOps Test Plans using direct REST API calls
- Saves data in two formats:
  - **JSON files**: Structured data in `json_output/` folder
  - **Excel files**: Spreadsheet format in `excel_output/` folder
- Each Excel file contains:
  - Test Cases sheet with detailed test case information
  - Summary sheet with metadata
  - Auto-adjusted column widths for better readability

## Requirements

- Python 3.7+
- Azure DevOps Personal Access Token (PAT) with Test Plans read permissions
- Required packages (install with `pip install -r requirements.txt`):
  - requests
  - pandas
  - openpyxl

## Setup

1. **Create a Personal Access Token (PAT)** in Azure DevOps:

   - Go to Azure DevOps → User Settings → Personal Access Tokens
   - Create a new token with "Test Plans (Read)" permissions
   - Copy the token value

2. **Set environment variable**:

   ```powershell
   $env:AZURE_DEVOPS_PAT = "your_pat_token_here"
   ```

3. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage (All Suites)

```powershell
python extract_test_cases.py
```

This extracts all suites from 1410044 to 1410100 (57 suites total).

### Extract Specific Suites

```powershell
# Extract only suite 1410044
python extract_test_cases.py --suites 1410044

# Extract multiple specific suites
python extract_test_cases.py --suites 1410044 1410045 1410050

# Extract many specific suites
python extract_test_cases.py --suites 1410044 1410045 1410046 1410047 1410048
```

### Extract Suite Range

```powershell
# Extract suites 1410044 to 1410048
python extract_test_cases.py --range 1410044 1410048

# Extract suites 1410090 to 1410100
python extract_test_cases.py --range 1410090 1410100
```

### Custom Output Directories

```powershell
# Use custom output directories
python extract_test_cases.py --json-dir my_json_files --excel-dir my_excel_files

# Extract specific suites to custom directories
python extract_test_cases.py --suites 1410044 1410045 --json-dir test_json --excel-dir test_excel
```

### Help

```powershell
python extract_test_cases.py --help
```

## Output Structure

The script creates two output folders (default names, can be customized):

### `json_output/` (or custom JSON directory)

- Contains JSON files for each processed suite: `Suite_[ID]_TestCases.json`
- Example files: `Suite_1410044_TestCases.json`, `Suite_1410045_TestCases.json`, etc.
- Each file contains structured test case data with test plan info, suite details, and summary

### `excel_output/` (or custom Excel directory)

- Contains Excel files for each processed suite: `Suite_[ID]_TestCases.xlsx`
- Example files: `Suite_1410044_TestCases.xlsx`, `Suite_1410045_TestCases.xlsx`, etc.
- Each Excel file has two sheets:
  - **Test Cases**: Detailed test case information
  - **Summary**: Metadata and summary statistics

## Data Fields

Each test case includes:

- Test Case ID
- Test Case Name
- Number of Steps
- Assigned To
- Assigned To

## Error Handling

- The script gracefully handles missing dependencies (pandas/openpyxl)
- If pandas is not installed, only JSON files will be created
- API timeouts and errors are logged with retry logic
- Empty suites are handled properly

## Configuration

### Command Line Options

- `--suites [IDs]`: Extract specific suite IDs (e.g., `--suites 1410044 1410045`)
- `--range START END`: Extract suite ID range (e.g., `--range 1410044 1410048`)
- `--json-dir DIR`: Custom JSON output directory (default: "json_output")
- `--excel-dir DIR`: Custom Excel output directory (default: "excel_output")

### Default Behavior

- Without arguments: Extracts suites 1410044 to 1410100 (57 suites total)
- Default output directories: "json_output" and "excel_output"

## Troubleshooting

1. **"AZURE_DEVOPS_PAT environment variable not set"**:

   - Make sure you've set the PAT token environment variable
   - Restart your terminal/command prompt after setting the variable

2. **"pandas not installed" warning**:

   - Install pandas and openpyxl: `pip install pandas openpyxl`
   - Or install all requirements: `pip install -r requirements.txt`

3. **API Permission Errors**:

   - Verify your PAT token has "Test Plans (Read)" permissions
   - Check if your token has expired

4. **Empty Results**:
   - Verify the suite IDs exist in your Azure DevOps project
   - Check your permissions to access the test plans
