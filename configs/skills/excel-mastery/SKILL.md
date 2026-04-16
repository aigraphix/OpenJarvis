---
name: excel-mastery
description: Advanced local spreadsheet processing using Pandas and OpenPyXL.
homepage: https://pandas.pydata.org/
metadata: {
    "nexus": {
        "emoji": "📊",
        "requires": { "libs": ["pandas", "openpyxl"] },
    },
}
---

# Excel Mastery (Local)

This skill provides powerful, local-first spreadsheet manipulation. No cloud
APIs required.

## Capabilities

- **Read/Write XLSX**: Full support for `.xlsx` and `.csv` files.
- **Data Analysis**: Leveraging Pandas for filtering, sorting, and aggregating
  data.
- **Formatting**: Using OpenPyXL for styling cells and adding charts.
- **System Integration**: Bridging automation results into structured reports.

## Usage

Run the excel bridge task: `python3 runner.py task_excel_bridge.py --run`

## Governance

- **Privacy**: All data processing happens in memory and on disk locally.
- **Superpower**: Perfect for handling high-volume logs or system audits.
