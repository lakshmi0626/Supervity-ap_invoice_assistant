import streamlit as st
import json
import os
from extraction_service import extract_invoice_data
from reconciliation import reconcile_invoice
from chat_assistant import answer_reviewer_query

st.set_page_config(page_title="AP Invoice Exception Assistant", layout="wide")

st.title("🧾 AP Invoice Exception Assistant")
st.write("Upload an invoice to automatically reconcile line items against PO records and inquire about flagged exceptions.")

# API Key Sidebar Configuration
api_key = st.sidebar.text_input("Gemini API Key", type="password", value=os.environ.get("GEMINI_API_KEY", ""))

if not api_key:
    st.warning("Please enter your Gemini API Key in the sidebar to proceed.")
    st.stop()

# Load Mock PO Data
with open("mock_po.json", "r") as f:
    mock_po = json.load(f)

# Sidebar PO Viewer
with st.sidebar:
    st.subheader("Reference Purchase Order")
    st.json(mock_po)

# File Upload Section
uploaded_file = st.file_uploader("Upload Vendor Invoice (PDF or Image)", type=["pdf", "png", "jpg", "jpeg"])

if uploaded_file:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Uploaded Document")
        if uploaded_file.type == "application/pdf":
            st.info("PDF Uploaded successfully.")
        else:
            st.image(uploaded_file, use_container_width=True)

    with col2:
        st.subheader("Automated Reconciliation Log")
        
        with st.spinner("Extracting invoice items & running rules engine..."):
            file_bytes = uploaded_file.read()
            
            # Step 1: Extraction
            extracted_schema = extract_invoice_data(file_bytes, uploaded_file.type, api_key)
            extracted_dict = extracted_schema.model_dump()
            
            # Step 2: Reconciliation Logic
            exceptions = reconcile_invoice(extracted_dict, mock_po)

        # Display Exception Flags
        if exceptions:
            st.error(f"⚠️ Flagged {len(exceptions)} Exception(s)!")
            st.dataframe(exceptions, use_container_width=True)
        else:
            st.success("✅ Invoice fully reconciled! No mismatches detected.")

        with st.expander("View Raw Extracted JSON"):
            st.json(extracted_dict)

    st.divider()

    # Step 3: Audit Assistant RAG Chat Interface
    st.subheader("💬 Reviewer Audit Chat Assistant")
    st.caption("Ask questions about flagged exceptions (e.g., 'Why was line item #1 flagged?' or 'What is wrong with invoice #123?')")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if user_query := st.chat_input("Ask a question about this audit..."):
        st.session_state.messages.append({"role": "user", "content": user_query})
        st.chat_message("user").write(user_query)

        with st.spinner("Analyzing exceptions..."):
            answer = answer_reviewer_query(user_query, extracted_dict, exceptions, api_key)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.chat_message("assistant").write(answer)