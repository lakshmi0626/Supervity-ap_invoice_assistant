def reconcile_invoice(extracted_data: dict, po_data: dict) -> list: 
    """Compares extracted invoice data against reference purchase order data 
 
    and returns a list of flagged exceptions. 
    """ 
    exceptions = [] 
 
    # Map PO items by description for easy lookup 
    po_items = { 
        item["item_description"].lower(): item 
        for item in po_data.get("line_items", []) 
    } 
 
    # Extract invoice items 
    invoice_items = extracted_data.get("line_items", []) 
 
    for item in invoice_items: 
        desc = item.get("item_description", "") 
        desc_lower = desc.lower() 
 
        actual_qty = float(item.get("quantity", 0)) 
        actual_price = float(item.get("unit_price", 0)) 
        actual_total = float(item.get("line_total", 0)) 
        tax_val = float(item.get("tax", 0.0) or 0.0) 
 
        # 1. Item Match Check 
        if desc_lower not in po_items: 
            exceptions.append( 
                { 
                    "type": "UNMATCHED_ITEM", 
                    "field": f"line_items['{desc}']", 
                    "source_val": desc, 
                    "expected_val": "Item on Purchase Order", 
                    "explanation": ( 
                        f"Item '{desc}' on invoice was not found on Reference" 
                        " PO." 
                    ), 
                } 
            ) 
            continue 
 
        po_item = po_items[desc_lower] 
        expected_qty = float(po_item.get("quantity", 0)) 
        expected_price = float(po_item.get("unit_price", 0)) 
 
        # 2. Quantity Variance Check 
        if actual_qty != expected_qty: 
            exceptions.append( 
                { 
                    "type": "QUANTITY_MISMATCH", 
                    "field": f"line_items['{desc}'].quantity", 
                    "source_val": str(actual_qty), 
                    "expected_val": str(expected_qty), 
                    "explanation": ( 
                        f"Quantity mismatch for '{desc}'. Invoiced" 
                        f" {actual_qty}, expected {expected_qty}." 
                    ), 
                } 
            ) 
 
        # 3. Price Variance Check 
        if actual_price != expected_price: 
            exceptions.append( 
                { 
                    "type": "PRICE_MISMATCH", 
                    "field": f"line_items['{desc}'].unit_price", 
                    "source_val": f"${actual_price:.2f}", 
                    "expected_val": f"${expected_price:.2f}", 
                    "explanation": ( 
                        f"Unit price mismatch for '{desc}'. Invoiced" 
                        f" ${actual_price:.2f}, expected ${expected_price:.2f}." 
                    ), 
                } 
            ) 
 
        # 4. Math Calculation Check 
        subtotal = round(actual_qty * actual_price, 2) 
        expected_total = round(subtotal + tax_val, 2) 
 
        if ( 
            abs(actual_total - subtotal) > 0.01 
            and abs(actual_total - expected_total) > 0.01 
        ): 
            exceptions.append( 
                { 
                    "type": "CALCULATION_ERROR", 
                    "field": f"line_items['{desc}'].line_total", 
                    "source_val": f"${actual_total:.2f}", 
                    "expected_val": f"${subtotal:.2f}", 
                    "explanation": ( 
                        f"Line total calculation mismatch for '{desc}'." 
                        f" Invoiced ${actual_total:.2f}, calculated subtotal" 
                        f" ${subtotal:.2f}." 
                    ), 
                } 
            ) 
 
    # ENSURE THIS RETURN STATEMENT IS INDENTED INSIDE THE FUNCTION 
    return exceptions 
