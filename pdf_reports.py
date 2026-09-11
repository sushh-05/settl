from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io
from datetime import date

def create_reminder_pdf(message_text):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=60, leftMargin=60,
                            topMargin=60, bottomMargin=60)
    styles = getSampleStyleSheet()
    body_style = styles['Normal']
    body_style.leading = 18

    elements = []
    for line in message_text.split('\n'):
        text = line.strip() if line.strip() else '&nbsp;'
        elements.append(Paragraph(text, body_style))

    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

def generate_invoice_report(invoice, buyer, business, payments, reminders):
    """Generate a comprehensive PDF report for an invoice using ReportLab."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    h2_style = styles['Heading2']
    normal_style = styles['Normal']
    
    elements = []
    
    # Title
    elements.append(Paragraph(f"Payment Follow-up Report: {invoice['invoice_number']}", title_style))
    elements.append(Spacer(1, 20))
    
    # Business Details
    elements.append(Paragraph("<b>Business Details</b>", h2_style))
    biz_name = business['business_name'] if business else "N/A"
    elements.append(Paragraph(f"Name: {biz_name}", normal_style))
    elements.append(Spacer(1, 10))
    
    # Buyer Details
    elements.append(Paragraph("<b>Buyer Details</b>", h2_style))
    elements.append(Paragraph(f"Name: {buyer['buyer_name']}", normal_style))
    elements.append(Spacer(1, 10))
    
    # Invoice Details
    elements.append(Paragraph("<b>Invoice Details</b>", h2_style))
    
    # Calculate overdue days
    today = date.today()
    due_date = invoice['due_date']
    if isinstance(due_date, str):
        from datetime import datetime
        due_date = datetime.strptime(due_date, "%Y-%m-%d").date()
        
    overdue_days = (today - due_date).days if today > due_date else 0
    
    inv_data = [
        ["Invoice Number", invoice['invoice_number']],
        ["Invoice Date", str(invoice['invoice_date'])],
        ["Due Date", str(invoice['due_date'])],
        ["Invoice Amount", f"Rs. {invoice['invoice_amount']:,.2f}"],
        ["Amount Paid", f"Rs. {invoice['amount_paid']:,.2f}"],
        ["Balance Due", f"Rs. {invoice['balance_due']:,.2f}"],
        ["Status", invoice['status']],
        ["Overdue Days", str(overdue_days) if overdue_days > 0 else "Not overdue"]
    ]
    
    inv_table = Table(inv_data, colWidths=[150, 250])
    inv_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(inv_table)
    elements.append(Spacer(1, 20))
    
    # Payment History
    elements.append(Paragraph("<b>Payment History</b>", h2_style))
    if payments:
        pay_data = [["Date", "Amount", "Mode", "Reference"]]
        for p in payments:
            pay_data.append([
                str(p['payment_date']), 
                f"Rs. {p['amount']:,.2f}", 
                p['payment_mode'] or "N/A", 
                p['reference_number'] or "N/A"
            ])
        pay_table = Table(pay_data, colWidths=[100, 100, 100, 150])
        pay_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(pay_table)
    else:
        elements.append(Paragraph("No payments recorded.", normal_style))
    elements.append(Spacer(1, 20))
    
    # Reminder History
    elements.append(Paragraph("<b>Reminder History</b>", h2_style))
    if reminders:
        rem_data = [["Date", "Type", "Channel"]]
        for r in reminders:
            # Extract just the date part if it's a timestamp
            sent_date = str(r['sent_date']).split(' ')[0]
            rem_data.append([sent_date, r['reminder_type'], r['channel']])
        rem_table = Table(rem_data, colWidths=[100, 150, 100])
        rem_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(rem_table)
    else:
        elements.append(Paragraph("No reminders sent.", normal_style))
    elements.append(Spacer(1, 20))
    
    # Document Checklist
    elements.append(Paragraph("<b>Document Checklist (For MSME Samadhaan Preparation)</b>", h2_style))
    
    has_invoice = "Yes" if invoice['document_path'] else "No"
    has_payment = "Yes" if invoice['amount_paid'] > 0 else "No"
    has_reminders = "Yes" if reminders else "No"
    
    check_data = [
        ["[ ] Invoice", has_invoice],
        ["[ ] Purchase order/work order", "Pending"],
        ["[ ] Delivery proof", "Pending"],
        ["[ ] Completion proof", "Pending"],
        ["[ ] Payment record", has_payment],
        ["[ ] Reminder history", has_reminders],
        ["[ ] Buyer communication", "Pending"],
        ["[ ] Udyam certificate", "Pending"]
    ]
    
    check_table = Table(check_data, colWidths=[250, 100])
    check_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(check_table)
    
    # Build PDF
    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes
