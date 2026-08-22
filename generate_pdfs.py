from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_invoice_pdf(filename, inv_num, po_num, items, tax, total):
    c = canvas.Canvas(filename, pagesize=letter)
    
    # Header
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, 750, "VENDOR INVOICE")
    
    c.setFont("Helvetica", 10)
    c.drawString(50, 725, "Vendor: Acme Industrial Supplies")
    c.drawString(50, 710, f"Invoice Number: {inv_num}")
    c.drawString(50, 695, f"PO Reference: {po_num}")
    
    # Table Headers
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, 650, "Item Description")
    c.drawString(250, 650, "Qty")
    c.drawString(320, 650, "Unit Price")
    c.drawString(420, 650, "Line Total")
    c.line(50, 642, 520, 642)
    
    # Table Content
    y = 620
    c.setFont("Helvetica", 10)
    for item in items:
        c.drawString(50, y, item["desc"])
        c.drawString(250, y, str(item["qty"]))
        c.drawString(320, y, f"${item['price']:.2f}")
        c.drawString(420, y, f"${item['total']:.2f}")
        y -= 25
        
    c.line(50, y+10, 520, y+10)
    c.drawString(320, y - 10, f"Tax: ${tax:.2f}")
    c.setFont("Helvetica-Bold", 11)
    c.drawString(320, y - 30, f"Total Amount Due: ${total:.2f}")
    
    c.save()
    print(f"Generated {filename}")

# 1. Mismatched Invoice PDF (Use this to test exception flags & chat)
mismatched_items = [
    {"desc": "Ergonomic Office Chair", "qty": 5, "price": 175.00, "total": 875.00}, # Price mismatch ($175 vs $150)
    {"desc": "Mechanical Keyboard", "qty": 12, "price": 80.00, "total": 1000.00}    # Qty mismatch (12 vs 10) + Total Math Error
]
create_invoice_pdf("mismatched_invoice.pdf", "INV-2026-001", "PO-9912", mismatched_items, tax=50.00, total=1925.00)

# 2. Fully Matching Invoice PDF (Use this to test pass-through reconciliation)
matching_items = [
    {"desc": "Ergonomic Office Chair", "qty": 5, "price": 150.00, "total": 750.00},
    {"desc": "Mechanical Keyboard", "qty": 10, "price": 80.00, "total": 800.00}
]
create_invoice_pdf("matching_invoice.pdf", "INV-2026-002", "PO-9912", matching_items, tax=124.00, total=1674.00)