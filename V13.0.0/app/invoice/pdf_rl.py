from pathlib import Path
from typing import List, Optional, Dict, Any

# PDF generator using reportlab (no Excel dependency)

def generate_pdf_invoice(out_path: Path,
                         employee_name: str,
                         items: List[Dict[str, Any]],
                         currency: str = "GBP",
                         invoice_no: Optional[str] = None,
                         invoice_date: Optional[str] = None,
                         call_off: Optional[str] = None,
                         company_name: str = "ABZ Serviços Ltda",
                         client_name: Optional[str] = "Omega") -> Path:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import mm
        from reportlab.pdfgen import canvas
        from reportlab.platypus import Table, TableStyle
    except Exception as e:
        raise RuntimeError("ReportLab is required. Please install with: pip install reportlab") from e

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    c = canvas.Canvas(str(out_path), pagesize=A4)
    W, H = A4

    # Header
    y = H - 30*mm
    c.setFont("Helvetica-Bold", 18)
    c.drawString(20*mm, y, "INVOICE")
    c.setFont("Helvetica", 10)
    y -= 8*mm
    c.drawString(20*mm, y, f"Company: {company_name}")
    y -= 5*mm
    c.drawString(20*mm, y, f"Client: {client_name or ''}")

    # Meta (right side)
    meta_y = H - 25*mm
    c.setFont("Helvetica", 10)
    if invoice_no:
        c.drawRightString(W-20*mm, meta_y, f"Invoice No: {invoice_no}")
        meta_y -= 5*mm
    if invoice_date:
        c.drawRightString(W-20*mm, meta_y, f"Date: {invoice_date}")
        meta_y -= 5*mm
    if call_off:
        c.drawRightString(W-20*mm, meta_y, f"Call-Off: {call_off}")
        meta_y -= 5*mm

    # Employee title
    y -= 10*mm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(20*mm, y, employee_name)

    # Table data
    y -= 8*mm
    data = [["Description", "Unit", "Qty", "Amount"]]
    subtotal = 0.0
    for it in items:
        desc = str(it.get("description", ""))
        unit = it.get("unit_price")
        qty = it.get("quantity")
        amt = it.get("final")
        if isinstance(amt, (int, float)):
            subtotal += float(amt)
        def fmt_unit(x):
            if x is None or x == "":
                return ""
            if isinstance(x, (int, float)):
                return f"{currency} {x:,.2f}"
            return str(x)
        def fmt_qty(x):
            if x is None or x == "":
                return ""
            if isinstance(x, (int, float)):
                return f"{x:g}"
            return str(x)
        def fmt_amt(x):
            if x is None or x == "":
                return ""
            if isinstance(x, (int, float)):
                return f"{currency} {x:,.2f}"
            return str(x)
        data.append([desc, fmt_unit(unit), fmt_qty(qty), fmt_amt(amt)])

    # Build table
    table = Table(data, colWidths=[90*mm, 25*mm, 20*mm, 35*mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.whitesmoke),
        ("TEXTCOLOR", (0,0), (-1,0), colors.black),
        ("ALIGN", (1,1), (-1,-1), "RIGHT"),
        ("ALIGN", (0,0), (0,-1), "LEFT"),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("GRID", (0,0), (-1,-1), 0.25, colors.lightgrey),
        ("LINEBELOW", (0,0), (-1,0), 0.5, colors.grey),
    ]))

    tw, th = table.wrapOn(c, W-40*mm, H)
    table.drawOn(c, 20*mm, y - th)

    # Totals
    ty = (y - th) - 12
    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(W-20*mm, ty, f"Subtotal: {currency} {subtotal:,.2f}")
    ty -= 6*mm
    c.drawRightString(W-20*mm, ty, f"Total: {currency} {subtotal:,.2f}")

    # Footer note
    from reportlab.lib import colors as _colors
    c.setFont("Helvetica", 8)
    c.setFillColor(_colors.grey)
    c.drawString(20*mm, 12*mm, "All amounts in GBP. Thank you for your business.")

    c.showPage()
    c.save()
    return out_path

