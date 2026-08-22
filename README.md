# AP Invoice Exception Assistant

## Problem
AI Employee that extracts invoice data, compares it against a purchase order,
and identifies price, quantity, and tax mismatches.

## Features
- Invoice PDF/image upload
- PO upload
- Structured line-item extraction
- Price mismatch detection
- Quantity mismatch detection
- Tax mismatch detection
- Source-grounded explanations
- Chat interface

## Tech Stack
- Python
- Streamlit
- OCR/document extraction
- LLM
- SQLite/JSON
- Python reconciliation engine

## Architecture
Invoice/PO
    ↓
Document Extraction
    ↓
Structured JSON
    ↓
Reconciliation Engine
    ↓
Exceptions
    ↓
AI Explanation
    ↓
Chat Interface

## Setup

```bash
git clone YOUR_REPOSITORY_URL
cd supervity-ap-invoice-assistant

python -m venv venv

# Windows
venv\Scripts\activate

pip install -r requirements.txt

streamlit run app.py
