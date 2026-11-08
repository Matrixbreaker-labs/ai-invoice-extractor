# AI-Powered Invoice Data Extraction Pipeline

A highly resilient, fault-tolerant batch processing data pipeline designed to automate financial data extraction from unstructured supplier invoices (PDFs, scans, text dumps). Powered by the official Google GenAI SDK [†] and strict Pydantic JSON schema constraints, the tool flattens diverse document layouts into clean, normalized tabular formats (.csv / .xlsx) without any brittle Regex models.

## 🛠️ Operational Capabilities
* **Strict Type Validation:** Clamps API outputs into rigid datatypes (e.g., float numbers for currency, YYYY-MM-DD standard for dates).
* **Fault-Tolerant Processing:** Localized try-except isolation ensures that corrupted files are logged and skipped without breaking the entire batch loop.
* **Automated Audit Flagging:** Automatically tags records with missing critical fields as `MANUAL REVIEW REQUIRED` for rapid filtering.

## 📊 Sample Execution Matrix Output

| processed_filename | supplier_name | invoice_number | invoice_date | due_date | subtotal | tax | total_amount | currency | audit_status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| invoice_dhl_digital.pdf | DHL EXPRESS | DHL-2026-8812 | 2026-10-22 | 2026-11-05 | 3000.0 | 300.0 | 3300.0 | USD | AUDIT PASSED |
| invoice_scanned_corrupted.pdf | CORRUPTED FILE ERROR | ERROR | None | None | None | None | None | None | CRITICAL FILE ERROR |
| invoice_maersk_missing_fields.pdf | MAERSK LINE | MSK-9901A | None | None | None | 150.0 | None | BDT | MANUAL REVIEW REQUIRED |

## 🚀 Local Deployment Setup

```bash
pip install google-genai pydantic pandas openpyxl tabulate
export GEMINI_API_KEY="your_free_gemini_api_key"
python main.py
```
