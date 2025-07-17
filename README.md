# Financial Statement Automation Tool

This is a Python project co-developed by me (Yufei Hu) and [Wokii](https://github.com/wokii) in 2023.  
It was designed to automate the analysis and reporting of financial data using structured programming and financial logic.

## What It Does
- Parses two-year financial statement data from a CSV file
- Calculates key financial ratios, including:
  - Current Ratio
  - Debt-to-Equity Ratio
  - Debt Service Coverage Ratio
- Generates:
  - A new CSV file including absolute and percentage changes
  - A narrative TXT report in plain English describing financial movements

## How to Use

1. Prepare a `sample.csv` file with this structure:

   | Name                        | Current Year | Last Year |
   |-----------------------------|--------------|-----------|
   | Revenue                     | 100.0        | 90.0      |
   | Profit                      | 20.0         | 18.0      |
   | Assets                      | 300.0        | 250.0     |
   | ...                         | ...          | ...       |

2. Run the script:

   ```bash
   python main.py
