# Invoice Processor

[中文版](README_CN.md)

Batch processing tool for invoice PDFs. Automatically extracts invoice information, renames files, and generates Excel summaries.

## Features

- **Extract invoice info** — Auto-recognize invoice number, date, type, amount, company name, tax ID, license plate from PDF
- **Validate company info** — Compare company name and tax ID against expected values
- **Smart rename** — Rename PDFs by `type-amount` convention, handle duplicates automatically
- **Excel summary** — Export all invoice data to Excel with per-folder sheets
- **Simplify filenames** — Batch remove prefix numbers from PDF filenames
- **GUI** — Chinese GUI built with Gooey, tabbed navigation

## Install

```bash
pip install pdfplumber openpyxl gooey
```

## Usage

```bash
python main.py
```

A GUI window will open with two tabs:

1. **Initialize PDF & Generate Excel** — Select a PDF folder, auto-process and output to `folder_output`
2. **Simplify PDF Filenames** — Select a folder, batch simplify PDF filenames

## Configuration

Edit `config.json` to set company info:

```json
{
    "expected_company": "Your Company Name",
    "expected_tax_id": "Your Tax ID",
    "excel_filename": "Invoice Summary.xlsx"
}
```

| Field | Description |
|-------|-------------|
| `expected_company` | Company name to validate. Leave empty to skip validation |
| `expected_tax_id` | Tax ID to validate. Leave empty to skip validation |
| `excel_filename` | Output Excel filename |

## Output Structure

```
folder_output/
├── subfolder1/
│   ├── Charging Fee-123.45.pdf
│   ├── Accommodation-200.00.pdf
│   └── Invoice Summary.xlsx
└── subfolder2/
    └── ...
```

## Build EXE

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name invoice-processor main.py
```

The executable will be in `dist/invoice-processor.exe`.

## License

MIT
