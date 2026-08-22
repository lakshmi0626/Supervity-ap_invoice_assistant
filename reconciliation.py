def reconcile_invoice(invoice_data: dict, po_data: dict) -> list:
    """
    Compare invoice data against purchase order data
    and return a list of reconciliation exceptions.
    """

    exceptions = []

    # ---------------------------------------------------------
    # 1. PO Number Match Check
    # ---------------------------------------------------------
    invoice_po = str(invoice_data.get("po_number", "")).strip()
    po_number = str(po_data.get("po_number", "")).strip()

    if invoice_po != po_number:
        exceptions.append({
            "type": "PO_MISMATCH",
            "field": "po_number",
            "source_val": invoice_po,
            "expected_val": po_number,
            "explanation": (
                f"Invoice references PO {invoice_po}, "
                f"but matched PO is {po_number}."
            )
        })

    # ---------------------------------------------------------
    # Build PO item lookup
    # ---------------------------------------------------------
    po_items = {}

    for item in po_data.get("line_items", []):
        description = str(
            item.get("item_description", "")
        ).strip().lower()

        if description:
            po_items[description] = item

    # ---------------------------------------------------------
    # 2-4. Line Item Checks
    # ---------------------------------------------------------
    for item in invoice_data.get("line_items", []):

        desc = str(item.get("item_description", "")).strip()
        desc_key = desc.lower()

        # -----------------------------------------------------
        # Unmatched Item Check
        # -----------------------------------------------------
        if desc_key not in po_items:
            exceptions.append({
                "type": "UNMATCHED_ITEM",
                "field": f"line_items['{desc}']",
                "source_val": desc,
                "expected_val": "Not on PO",
                "explanation": (
                    f"Item '{desc}' does not exist on "
                    f"Purchase Order {po_number}."
                )
            })
            continue

        po_item = po_items[desc_key]

        # Safely read values
        invoice_price = float(item.get("unit_price", 0))
        po_price = float(po_item.get("unit_price", 0))

        invoice_qty = float(item.get("quantity", 0))
        po_qty = float(po_item.get("quantity", 0))

        invoice_tax = float(item.get("tax", 0))
        invoice_line_total = float(item.get("line_total", 0))

        # -----------------------------------------------------
        # 2. Price Mismatch Check
        # -----------------------------------------------------
        if round(invoice_price, 2) != round(po_price, 2):

            if invoice_price > po_price:
                explanation = (
                    f"Invoice unit price (${invoice_price:.2f}) "
                    f"exceeds PO price (${po_price:.2f})."
                )
            else:
                explanation = (
                    f"Invoice unit price (${invoice_price:.2f}) "
                    f"is lower than PO price (${po_price:.2f})."
                )

            exceptions.append({
                "type": "PRICE_MISMATCH",
                "field": f"line_items['{desc}'].unit_price",
                "source_val": f"${invoice_price:.2f}",
                "expected_val": f"${po_price:.2f}",
                "explanation": explanation
            })

        # -----------------------------------------------------
        # 3. Quantity Mismatch Check
        # -----------------------------------------------------
        if invoice_qty > po_qty:
            exceptions.append({
                "type": "QTY_MISMATCH",
                "field": f"line_items['{desc}'].quantity",
                "source_val": str(invoice_qty),
                "expected_val": str(po_qty),
                "explanation": (
                    f"Invoiced quantity ({invoice_qty:g}) exceeds "
                    f"approved PO quantity ({po_qty:g})."
                )
            })

        # -----------------------------------------------------
        # 4. Tax / Calculation Check
        # -----------------------------------------------------
        # Change this:
# expected_total = round((item["quantity"] * item["unit_price"]) + item["tax"], 2)

# To this:
subtotal = round(item["quantity"] * item["unit_price"], 2)
tax_val = item.get("tax", 0.0) or 0.0
expected_total = round(subtotal + tax_val, 2)

# Allow a small tolerance check or check subtotal directly:
if abs(actual_total - subtotal) > 0.01 and abs(actual_total - expected_total) > 0.01:
    exceptions.append({
        "type": "CALCULATION_ERROR",
        "field": f"line_items['{desc}'].line_total",
        "source_val": f"${actual_total:.2f}",
        "expected_val": f"${subtotal:.2f}",
        "explanation": f"Line total mismatch. Expected ${subtotal:.2f}, got ${actual_total:.2f}."
    })
    return exceptions