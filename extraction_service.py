import os
from typing import List
from pydantic import BaseModel
from google import genai
from google.genai import types

class LineItem(BaseModel):
    item_description: str
    quantity: float
    unit_price: float
    tax: float
    line_total: float

class InvoiceSchema(BaseModel):
    invoice_number: str
    po_number: str
    vendor_name: str
    line_items: List[LineItem]

def extract_invoice_data(file_bytes: bytes, mime_type: str, api_key: str) -> InvoiceSchema:
    """Sends invoice bytes to Gemini Flash and parses into structured Pydantic schema."""
    client = genai.Client(api_key=api_key)
    
    prompt = "Extract all line items, PO number, invoice number, and vendor name from this invoice."
    
    response = client.models.generate_content(
        model='gemini-3.6-flash',  # <-- USE THE SUPPORTED MODEL NAME HERE
        contents=[
            types.Part.from_bytes(data=file_bytes, mime_type=mime_type),
            prompt
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=InvoiceSchema,
        )
    )
    
    return InvoiceSchema.model_validate_json(response.text)