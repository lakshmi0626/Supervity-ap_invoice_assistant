from google import genai

def answer_reviewer_query(query: str, extracted_data: dict, exceptions: list, api_key: str) -> str:
    """Answers reviewer questions strictly grounded in extracted data and reconciliation findings."""
    client = genai.Client(api_key=api_key)
    
    system_prompt = f"""
    You are an AP Exceptions Audit Assistant. Your job is to explain why an invoice was flagged.
    Answer user queries using ONLY the metadata provided below.
    Always cite specific original fields (e.g., 'Invoiced Unit Price vs PO Unit Price') in your explanation.
    
    EXTRACTED INVOICE DATA:
    {extracted_data}
    
    FLAGGED EXCEPTIONS:
    {exceptions}
    """
    
    response = client.models.generate_content(
        model='gemini-3.6-flash',  # <-- USE THE SUPPORTED MODEL NAME HERE
        contents=[system_prompt, query]
    )
    return response.text