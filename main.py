# ===========================================================================
# 1. DEPENDENCY INITIALIZATION & ENVIRONMENT SETUP
# ===========================================================================
import os
import json
import time
import asyncio
import pandas as pd
from typing import List, Optional
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

# Initialize Gemini Client safely from system environment variables
def get_gemini_client() -> genai.Client:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("CRITICAL ERROR: Missing GEMINI_API_KEY environment variable.")
    return genai.Client(api_key=api_key)

# ===========================================================================
# 2. SCHEMA ARCHITECTURE (Strict Type-Safe Validation Constraints)
# ===========================================================================
class InvoiceDataSchema(BaseModel):
    supplier_name: str = Field(description="The formal name of the supplier or vendor issuing the invoice.")
    invoice_number: str = Field(description="The unique identification number of the invoice document.")
    invoice_date: Optional[str] = Field(None, description="The date the invoice was issued, formatted strictly as YYYY-MM-DD.")
    due_date: Optional[str] = Field(None, description="The payment due date, formatted strictly as YYYY-MM-DD.")
    subtotal: Optional[float] = Field(None, description="The invoice subtotal amount before taxes as a plain numeric float.")
    tax: Optional[float] = Field(None, description="The calculated tax amount as a plain numeric float.")
    total_amount: Optional[float] = Field(None, description="The absolute total billed invoice amount due as a plain numeric float.")
    currency: Optional[str] = Field(None, description="The ISO currency code or symbol specified (e.g., USD, EUR, BDT).")

class IngestionPayload(BaseModel):
    records: List[InvoiceDataSchema]

# ===========================================================================
# 3. AI COGNITIVE EXTRACTION NODE (Gemini Structured Outputs Integration)
# ===========================================================================
async def extract_invoice_via_gemini(file_id: int, filename: str, raw_invoice_content: str, client: genai.Client) -> Optional[dict]:
    """
    Ingests raw document logs and forces Gemini to return strict Pydantic validated objects.
    Implements internal error-trapping bounds to guarantee batch stability.
    """
    print(f"[*] [File-{file_id}] Extracting structural line items from: {filename}...")
    
    prompt = f"""
    You are an expert AI Accounting & Audit Controller. Analyze the following raw unstructured invoice text data.
    Extract the required fields exactly matching the structural layout fields specified.
    Convert all currency amounts into plain float numbers and normalize all dates into YYYY-MM-DD standard format.
    If a specific field cannot be found under any circumstances, leave it as null.
    
    Raw Document Data Payload:
    \"\"\"{raw_invoice_content}\"\"\"
    """
    
    try:
        # Enforcing structured generation constraints natively on active gemini-3.5-flash endpoint [†]
        response = await asyncio.to_thread(
            client.models.generate_content,
            model='gemini-3.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=IngestionPayload,
                temperature=0.1
            )
        )
        
        # Parse the structured JSON response string directly into the validation dict matrix
        audit_dict = json.loads(response.text)
        
        # -------------------------------------------------------------------
        # 4. INDUSTRIAL-GRADE FAULT FLAGGING LOGIC (Audit Verification)
        # -------------------------------------------------------------------
        if not audit_dict.get('total_amount') or not audit_dict.get('invoice_date'):
            audit_dict['audit_status'] = "MANUAL REVIEW REQUIRED"
            print(f"[!] [File-{file_id}] Warning: Missing critical financial records. Flagged row.")
        else:
            audit_dict['audit_status'] = "AUDIT PASSED"
            
        audit_dict['processed_filename'] = filename
        return audit_dict
        
    except Exception as e:
        print(f"[-] [File-{file_id}] Extraction Fault intercepted: {e}")
        return {
            "supplier_name": "CORRUPTED FILE ERROR",
            "invoice_number": "ERROR",
            "invoice_date": None,
            "due_date": None,
            "subtotal": None,
            "tax": None,
            "total_amount": None,
            "currency": None,
            "audit_status": "CRITICAL FILE ERROR - RESUBMIT",
            "processed_filename": filename
        }

# ===========================================================================
# 5. CORE BATCH PROCESSING ORCHESTRATOR
# ===========================================================================
async def main():
    try:
        client = get_gemini_client()
    except ValueError as e:
        print(e)
        return
    
    # Simulated multi-format invoice dumps representing your production target workspace
    simulated_invoice_folder = {
        "invoice_dhl_digital.pdf": """
            DHL EXPRESS GLOBAL LOGISTICS
            Invoice No: DHL-2026-8812
            Date of Issue: 22nd October 2026 | Payment Due: 05 Nov 2026
            Base Charges: $3,000.00
            VAT/Tax (10%): $300.00
            Total Net Amount Due: $3,300.00 USD
            Thank you for shipping with DHL.
        """,
        "invoice_scanned_corrupted.pdf": "### [CRITICAL RUNTIME ERROR: PDF stream corrupted / unreadable binary byte arrays] ###",
        "invoice_maersk_missing_fields.pdf": """
            MAERSK LINE INT SHIPPING
            Bill Ref: MSK-9901A
            Billing Center: Port of Chittagong Gateway
            Container Handled: 1x 40ft High Cube
            Tax Value: $150.00 BDT
            Note: Total due calculation delayed due to customs hold check.
        """
    }
    
    print(f"[*] Initializing Resilient Batch Engine across {len(simulated_invoice_folder)} document nodes...\n")
    
    compiled_dataset = []
    for idx, (filename, raw_content) in enumerate(simulated_invoice_folder.items(), start=1):
        extracted_record = await extract_invoice_via_gemini(idx, filename, raw_content, client)
        if extracted_record:
            compiled_dataset.append(extracted_record)
        await asyncio.sleep(4) # 4-second padding to respect free-tier constraints safely
            
    if compiled_dataset:
        df = pd.DataFrame(compiled_dataset)
        column_order = ["processed_filename", "supplier_name", "invoice_number", "invoice_date", "due_date", "subtotal", "tax", "total_amount", "currency", "audit_status"]
        df = df[column_order]
        
        output_csv = "supplier_invoices_extracted.csv"
        df.to_csv(output_csv, index=False)
        df.to_excel(output_csv.replace('.csv', '.xlsx'), index=False)
        
        print("\n" + "="*80)
        print(f"[++] DATA BATCH INGESTION COMPLETE! File saved directly to project directory.")
        print("="*80)

if __name__ == "__main__":
    asyncio.run(main())
