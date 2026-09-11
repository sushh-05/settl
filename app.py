import streamlit as st
from datetime import date, datetime
import database
import pandas as pd
import pdf_reports
import os
import ocr_service

def custom_css():
    return """
    /* ── Base & Typography ─────────────────────────────────────────── */
    html, body, [class*="css"] {
        font-family: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        font-size: 14px;
        color: #111827;
        background-color: #FAFAFA;
    }
    h1, h2, h3 { font-weight: 600 !important; color: #111827 !important; }
    h1 { font-size: 1.5rem; border-bottom: 1px solid #E5E7EB; padding-bottom: 12px; margin-bottom: 16px; }
    h2 { font-size: 1.25rem; }
    p, label, div { color: #4B5563; }
    /* High-specificity override for Streamlit's heading elements */
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3,
    [data-testid="stHeadingWithActionElements"] h1,
    [data-testid="stHeadingWithActionElements"] h2,
    [data-testid="stHeadingWithActionElements"] h3 {
        color: #111827 !important;
        font-weight: 600 !important;
    }

    /* ── Tabs ───────────────────────────────────────────────────────── */
    [data-testid="stTabs"] [role="tablist"] {
        border-bottom: 1px solid #E5E7EB;
        gap: 0;
    }
    [data-testid="stTabs"] [role="tab"] {
        font-size: 14px;
        font-weight: 500;
        color: #6B7280;
        padding: 8px 16px;
        border: none;
        border-bottom: 2px solid transparent;
        background: transparent;
        border-radius: 0;
        text-decoration: none !important;
    }
    [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
        color: #3B5BDB !important;
        border-bottom: 2px solid #3B5BDB !important;
        font-weight: 600;
        text-decoration: none !important;
    }
    [data-testid="stTabs"] [role="tab"]:hover {
        color: #3B5BDB;
        background: transparent;
    }

    /* ── Metrics bar ────────────────────────────────────────────────── */
    [data-testid="stMetric"] {
        background: transparent;
        border: none;
        border-right: 1px solid #E5E7EB;
        padding: 8px 24px 8px 0;
        box-shadow: none;
    }
    [data-testid="stMetric"]:last-child { border-right: none; }
    [data-testid="stMetricLabel"] {
        font-size: 11px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #6B7280;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.4rem;
        font-weight: 600;
        color: #111827;
        font-variant-numeric: tabular-nums;
    }

    /* ── Buttons ────────────────────────────────────────────────────── */
    .stButton > button {
        font-size: 13px;
        font-weight: 500;
        border-radius: 4px;
        border: 1px solid #D1D5DB;
        background: #FFFFFF;
        color: #374151;
        padding: 4px 12px;
        box-shadow: none;
        transition: background 0.15s ease;
    }
    .stButton > button:hover {
        background: #F3F4F6;
        border-color: #9CA3AF;
        color: #111827;
    }
    /* Primary submit button */
    [data-testid="stFormSubmitButton"] > button {
        background: #3B5BDB;
        color: #FFFFFF;
        border: none;
        font-weight: 600;
    }
    [data-testid="stFormSubmitButton"] > button:hover {
        background: #3451C7;
        color: #FFFFFF;
    }

    /* ── Radio filter bar ───────────────────────────────────────────── */
    [data-testid="stRadio"] > div {
        gap: 4px;
    }
    /* Remove bordered-box look from each radio option label */
    [data-testid="stRadio"] label {
        font-size: 13px;
        padding: 4px 10px;
        border-radius: 4px;
        border: none !important;
        background: transparent !important;
        cursor: pointer;
    }
    /* Accent color for selected radio dot */
    [data-testid="stRadio"] input[type="radio"]:checked + div {
        color: #3B5BDB;
    }
    [data-testid="stRadio"] input[type="radio"]:checked + div svg {
        fill: #3B5BDB !important;
        color: #3B5BDB !important;
    }

    /* ── Forms ──────────────────────────────────────────────────────── */
    [data-testid="stForm"] {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 6px;
        padding: 24px;
    }
    .stTextInput > label, .stNumberInput > label,
    .stDateInput > label, .stSelectbox > label,
    .stTextArea > label, .stFileUploader > label {
        font-size: 13px;
        font-weight: 500;
        color: #374151;
        margin-bottom: 4px;
    }
    .stTextInput input, .stNumberInput input {
        border: 1px solid #D1D5DB;
        border-radius: 4px;
        font-size: 14px;
        font-variant-numeric: tabular-nums;
    }

    /* ── Invoice table rows ─────────────────────────────────────────── */
    [data-testid="stHorizontalBlock"]:nth-child(even) {
        background-color: rgba(0,0,0,0.018);
    }
    [data-testid="stHorizontalBlock"] {
        border-bottom: 1px solid #F3F4F6;
        padding: 4px 0;
        align-items: center;
    }

    /* ── File uploader ──────────────────────────────────────────────── */
    [data-testid="stFileUploader"] {
        border: 1px dashed #D1D5DB;
        border-radius: 4px;
        padding: 12px;
        background: #F9FAFB;
    }

    /* ── Divider ────────────────────────────────────────────────────── */
    hr { border: none; border-top: 1px solid #E5E7EB; margin: 16px 0; }

    /* ── Alerts / info boxes ────────────────────────────────────────── */
    [data-testid="stAlert"] {
        border-radius: 4px;
        border-left-width: 3px;
        font-size: 13px;
    }
    """

def generate_reminder_text(reminder_type, language, invoice, business_name):
    # Format values
    buyer_name = invoice['buyer_name']
    invoice_number = invoice['invoice_number']
    balance_due = f"{invoice['balance_due']:,.2f}"
    due_date = invoice['due_date']
    
    if language == "Hindi":
        if reminder_type == "Friendly reminder":
            prefix = "यह एक विनम्र अनुस्मारक है कि आपका भुगतान जल्द ही देय है।\n\n"
        elif reminder_type == "Overdue reminder":
            prefix = "यह एक नोटिस है कि आपका भुगतान अब अतिदेय (overdue) है।\n\n"
        else: # Final review reminder
            prefix = "अति आवश्यक: यह आपके अतिदेय खाते के लिए अंतिम समीक्षा अनुस्मारक है।\n\n"
            
        return f"प्रिय {buyer_name},\n\n{prefix}यह चालान {invoice_number} के संबंध में एक अनुस्मारक है।\n₹{balance_due} की राशि बकाया है।\nभुगतान {due_date} को देय था।\n\nकृपया अपेक्षित भुगतान तिथि की पुष्टि करें।\n\nसादर,\n{business_name}"
        
    elif language == "Telugu":
        if reminder_type == "Friendly reminder":
            prefix = "మీ చెల్లింపు గడువు త్వరలో ముగుస్తుందని గుర్తుచేస్తున్నాము.\n\n"
        elif reminder_type == "Overdue reminder":
            prefix = "మీ చెల్లింపు గడువు ముగిసిందని తెలియజేస్తున్నాము.\n\n"
        else: # Final review reminder
            prefix = "అత్యవసరం: ఇది మీ ఖాతాకు సంబంధించిన తుది సమీక్ష రిమైండర్.\n\n"
            
        return f"ప్రియమైన {buyer_name},\n\n{prefix}ఇది ఇన్‌వాయిస్ {invoice_number} కి సంబంధించిన రిమైండర్.\n₹{balance_due} మొత్తం ఇంకా చెల్లించాల్సి ఉంది.\nచెల్లింపు గడువు తేదీ {due_date}.\n\nదయచేసి మీరు చెల్లించగలిగే తేదీని నిర్ధారించండి.\n\nగౌరవంతో,\n{business_name}"
        
    else: # English
        if reminder_type == "Friendly reminder":
            prefix = "Just a friendly reminder that your payment is due soon.\n\n"
        elif reminder_type == "Overdue reminder":
            prefix = "This is a notice that your payment is now overdue.\n\n"
        else: # Final review reminder
            prefix = "URGENT: This is a final review reminder for your severely overdue account.\n\n"
            
        return f"Dear {buyer_name},\n\n{prefix}This is a reminder regarding Invoice {invoice_number}.\nAn amount of ₹{balance_due} remains outstanding.\nThe payment was due on {due_date}.\n\nKindly confirm the expected payment date.\n\nRegards,\n{business_name}"

@st.dialog("Generate Reminder")
def reminder_dialog(invoice):
    st.write(f"**Invoice:** {invoice['invoice_number']} | **Buyer:** {invoice['buyer_name']}")
    
    reminder_type = st.selectbox("Reminder Type", ["Friendly reminder", "Overdue reminder", "Final review reminder"])
    language = st.selectbox("Language", ["English", "Hindi", "Telugu"])
    
    # Fetch business name
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT business_name FROM businesses LIMIT 1")
    biz = cursor.fetchone()
    business_name = biz['business_name'] if biz else "Your Business"
    conn.close()
    
    message = generate_reminder_text(reminder_type, language, invoice, business_name)
    
    edited_message = st.text_area("Message Preview (Edit if needed)", value=message, height=250)
    
    st.info("💡 Tip: You can manually copy the text above to paste into WhatsApp or Email.")
    
    col1, col2 = st.columns(2)
    
    # Download PDF
    pdf_bytes = pdf_reports.create_reminder_pdf(edited_message)
    col1.download_button(
        label="📄 Download as PDF",
        data=pdf_bytes,
        file_name=f"Reminder_{invoice['invoice_number']}.pdf",
        mime="application/pdf"
    )
    
    # Mark as sent
    if col2.button("✅ Mark as Sent"):
        try:
            conn = database.get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO reminders (invoice_id, reminder_type, message, sent_date, channel, status)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP, 'Manual', 'Sent')
            ''', (invoice['id'], reminder_type, edited_message))
            conn.commit()
            conn.close()
            st.success("Reminder marked as sent!")
            st.rerun()
        except Exception as e:
            st.error(f"Error saving reminder: {e}")

@st.dialog("Document Checklist")
def checklist_dialog(invoice):
    st.write(f"**Invoice:** {invoice['invoice_number']} | **Buyer:** {invoice['buyer_name']}")
    st.caption("⚠️ **Preparation checklist—not legal advice**")
    st.write("For possible MSME Samadhaan preparation, ensure you have the following documents:")
    
    st.checkbox("Invoice", value=True if invoice['document_path'] else False)
    st.checkbox("Purchase order/work order")
    st.checkbox("Delivery proof")
    st.checkbox("Completion proof")
    st.checkbox("Payment record", value=True if invoice['amount_paid'] > 0 else False)
    st.checkbox("Reminder history")
    st.checkbox("Buyer communication")
    st.checkbox("Udyam certificate, if applicable")
    
    if st.button("Close"):
        st.rerun()

@st.dialog("Record Payment")
def record_payment_dialog(invoice):
    st.write(f"**Invoice:** {invoice['invoice_number']}")
    st.write(f"**Invoice Amount:** ₹{invoice['invoice_amount']:,.2f}")
    st.write(f"**Previous Payment:** ₹{invoice['amount_paid']:,.2f}")
    st.write(f"**Remaining Balance:** ₹{invoice['balance_due']:,.2f}")
    
    with st.form(f"payment_form_{invoice['id']}"):
        payment_amount = st.number_input("New Payment Amount", min_value=0.01, max_value=float(invoice['balance_due']), step=0.01)
        payment_date = st.date_input("Payment Date", value=date.today())
        payment_mode = st.selectbox("Payment Mode", ["Bank Transfer", "Cash", "UPI", "Cheque", "Other"])
        reference_number = st.text_input("Transaction Reference")
        notes = st.text_area("Notes")
        
        submit = st.form_submit_button("Save Payment")
        
        if submit:
            new_balance = invoice['balance_due'] - payment_amount
            new_amount_paid = invoice['amount_paid'] + payment_amount
            
            if isinstance(invoice['due_date'], str):
                due_date_obj = datetime.strptime(invoice['due_date'], "%Y-%m-%d").date()
            else:
                due_date_obj = invoice['due_date']
                
            today = date.today()
            
            if new_balance <= 0:
                new_status = "Paid"
            elif today > due_date_obj:
                new_status = "Overdue"
            elif new_amount_paid > 0:
                new_status = "Partially paid"
            else:
                new_status = "Due"
                
            try:
                conn = database.get_db_connection()
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO payments (invoice_id, amount, payment_date, payment_mode, reference_number, notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (invoice['id'], payment_amount, payment_date, payment_mode, reference_number, notes))
                
                cursor.execute('''
                    UPDATE invoices 
                    SET amount_paid = ?, balance_due = ?, status = ?
                    WHERE id = ?
                ''', (new_amount_paid, new_balance, new_status, invoice['id']))
                
                conn.commit()
                conn.close()
                
                st.success("Payment recorded successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error saving payment: {e}")

st.set_page_config(page_title="MSME Payment Assistant", layout="wide")
st.markdown(f"<style>{custom_css()}</style>", unsafe_allow_html=True)

# Ensure DB and tables exist on every cold start (critical for Streamlit Cloud)
database.init_db()

st.title("MSME Payment Assistant")

tab1, tab2 = st.tabs(["Dashboard", "Add Invoice"])

with tab1:
    st.header("Dashboard")
    
    try:
        conn = database.get_db_connection()
        cursor = conn.cursor()
        
        # Fetch Metrics
        cursor.execute('''
            SELECT 
                SUM(CASE WHEN status != 'Paid' THEN balance_due ELSE 0 END) as total_outstanding,
                SUM(CASE WHEN status = 'Overdue' THEN balance_due ELSE 0 END) as total_overdue,
                SUM(CASE WHEN status = 'Overdue' THEN 1 ELSE 0 END) as count_overdue,
                SUM(CASE WHEN status != 'Paid' AND due_date BETWEEN date('now') AND date('now', '+7 days') THEN 1 ELSE 0 END) as due_this_week
            FROM invoices
        ''')
        metrics = cursor.fetchone()
        
        cursor.execute("SELECT COUNT(*) as pending_reminders FROM reminders WHERE status = 'Pending'")
        reminders_metric = cursor.fetchone()
        
        total_outstanding = metrics['total_outstanding'] or 0.0
        total_overdue = metrics['total_overdue'] or 0.0
        count_overdue = metrics['count_overdue'] or 0
        due_this_week = metrics['due_this_week'] or 0
        pending_reminders = reminders_metric['pending_reminders'] or 0
        
        # Display Metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total Outstanding", f"₹{total_outstanding:,.2f}")
        col2.metric("Total Overdue", f"₹{total_overdue:,.2f}")
        col3.metric("Overdue Invoices", count_overdue)
        col4.metric("Due This Week", due_this_week)
        col5.metric("Pending Reminders", pending_reminders)
        
        st.divider()
        
        # Filters
        st.subheader("Invoices")
        filter_option = st.radio(
            "Filter by Status:",
            ["All", "Due", "Overdue", "Partially paid", "Paid"],
            horizontal=True
        )
        
        # Fetch Invoices
        query = '''
            SELECT i.id, i.invoice_number, i.invoice_date, b.buyer_name, i.balance_due, i.due_date, i.status, i.invoice_amount, i.amount_paid, i.document_path
            FROM invoices i
            JOIN buyers b ON i.buyer_id = b.id
        '''
        params = []
        
        if filter_option != "All":
            if filter_option == "Partially paid":
                query += " WHERE i.amount_paid > 0 AND i.status != 'Paid'"
            else:
                query += " WHERE i.status = ?"
                params.append(filter_option)
                
        query += " ORDER BY i.due_date ASC"
        
        cursor.execute(query, params)
        invoices = cursor.fetchall()
        conn.close()
        
        if invoices:
            # Render Table Header
            header_cols = st.columns([1.5, 2, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5])
            header_cols[0].markdown("**Invoice**")
            header_cols[1].markdown("**Buyer**")
            header_cols[2].markdown("**Balance**")
            header_cols[3].markdown("**Due Date**")
            header_cols[4].markdown("**Status**")
            header_cols[5].markdown("**Action**")
            header_cols[6].markdown("**Payment**")
            header_cols[7].markdown("**Checklist**")
            header_cols[8].markdown("**Report**")
            
            # Render Table Rows
            for inv in invoices:
                row_cols = st.columns([1.5, 2, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5])
                row_cols[0].write(inv['invoice_number'])
                row_cols[1].write(inv['buyer_name'])
                row_cols[2].write(f"₹{inv['balance_due']:,.2f}")
                row_cols[3].write(inv['due_date'])
                
                # Status badge pill
                status = inv['status']
                status_styles = {
                    'Overdue':        ('●', '#DC2626', '#FEF2F2'),
                    'Paid':           ('●', '#059669', '#ECFDF5'),
                    'Due':            ('●', '#D97706', '#FFFBEB'),
                    'Partially paid': ('●', '#B45309', '#FEF3C7'),
                }
                dot, fg, bg = status_styles.get(status, ('●', '#6B7280', '#F3F4F6'))
                row_cols[4].markdown(
                    f"<span style='background:{bg};color:{fg};padding:2px 8px;border-radius:4px;"
                    f"font-size:12px;font-weight:500;white-space:nowrap'>{dot} {status}</span>",
                    unsafe_allow_html=True
                )
                
                # Action Button
                if status != 'Paid':
                    if row_cols[5].button("Remind", key=f"remind_{inv['id']}"):
                        reminder_dialog(inv)
                else:
                    if row_cols[5].button("View", key=f"view_{inv['id']}"):
                        st.toast(f"Viewing {inv['invoice_number']}")
                        
                # Payment Button
                if status != 'Paid':
                    if row_cols[6].button("Record Payment", key=f"pay_{inv['id']}"):
                        record_payment_dialog(inv)
                        
                # Checklist Button
                if status == 'Overdue':
                    if row_cols[7].button("Checklist", key=f"check_{inv['id']}"):
                        checklist_dialog(inv)
                        
                # Report Button
                if row_cols[8].button("Report", key=f"report_{inv['id']}"):
                    try:
                        conn = database.get_db_connection()
                        cursor = conn.cursor()
                        
                        # Fetch buyer
                        cursor.execute("SELECT * FROM buyers WHERE buyer_name = ?", (inv['buyer_name'],))
                        buyer = cursor.fetchone()
                        
                        # Fetch business
                        cursor.execute("SELECT * FROM businesses LIMIT 1")
                        business = cursor.fetchone()
                        
                        # Fetch payments
                        cursor.execute("SELECT * FROM payments WHERE invoice_id = ? ORDER BY payment_date DESC", (inv['id'],))
                        payments = cursor.fetchall()
                        
                        # Fetch reminders
                        cursor.execute("SELECT * FROM reminders WHERE invoice_id = ? ORDER BY sent_date DESC", (inv['id'],))
                        reminders = cursor.fetchall()
                        
                        conn.close()
                        
                        # Convert sqlite3.Row objects to dicts to avoid "No item with that key" errors
                        # when accessing them in pdf_reports.py
                        inv_dict = dict(inv)
                        buyer_dict = dict(buyer) if buyer else {"buyer_name": inv['buyer_name']}
                        business_dict = dict(business) if business else {"business_name": "Your Business"}
                        payments_list = [dict(p) for p in payments] if payments else []
                        reminders_list = [dict(r) for r in reminders] if reminders else []
                        
                        pdf_bytes = pdf_reports.generate_invoice_report(inv_dict, buyer_dict, business_dict, payments_list, reminders_list)
                        
                        st.download_button(
                            label="Download PDF",
                            data=pdf_bytes,
                            file_name=f"payment-follow-up-{inv['invoice_number']}.pdf",
                            mime="application/pdf",
                            key=f"dl_report_{inv['id']}"
                        )
                    except Exception as e:
                        st.error(f"Error generating report: {e}")
        else:
            st.info("No invoices found for the selected filter.")
            
    except Exception as e:
        st.error(f"Error loading dashboard: {e}")

with tab2:
    st.header("Add New Invoice")
    
    uploaded_file = st.file_uploader("Upload invoice (Optional)", type=["pdf", "png", "jpg", "jpeg"])
    
    # Handle OCR Extraction
    if uploaded_file is not None and uploaded_file.name != st.session_state.get("last_uploaded_file"):
        st.session_state["last_uploaded_file"] = uploaded_file.name
        
        # Save temporarily for OCR
        os.makedirs("uploads", exist_ok=True)
        temp_path = os.path.join("uploads", "temp_" + uploaded_file.name)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        with st.spinner("Extracting details using OCR..."):
            try:
                raw_text = ocr_service.extract_text_from_file(temp_path)
                extracted_data = ocr_service.parse_invoice_text(raw_text)
                
                st.session_state["ocr_data"] = extracted_data
                st.session_state["ocr_raw_text"] = raw_text
                st.success("OCR Extraction complete! Please verify the details below.")
            except Exception as e:
                st.error(f"OCR failed: {e}")
                
    elif uploaded_file is None:
        st.session_state.pop("last_uploaded_file", None)
        st.session_state.pop("ocr_data", None)
        st.session_state.pop("ocr_raw_text", None)

    # Pre-fill form with OCR data if available
    ocr_data = st.session_state.get("ocr_data", {})
    
    if ocr_data:
        st.info("💡 **We extracted the following information. Please verify and edit if necessary before saving.**")
        if ocr_data.get("missing_fields"):
            st.warning(f"⚠️ **Missing fields:** {', '.join(ocr_data['missing_fields'])}")
        if ocr_data.get("confidence_notes"):
            st.caption(f"📝 **Notes:** {ocr_data['confidence_notes']}")
            
        with st.expander("View Raw Extracted Text"):
            st.text(st.session_state.get("ocr_raw_text", ""))
    
    with st.form("invoice_form"):
        buyer_name = st.text_input("Buyer Name", value=ocr_data.get("buyer_name") or "")
        invoice_number = st.text_input("Invoice Number", value=ocr_data.get("invoice_number") or "")
        
        # Try to parse dates, fallback to today
        inv_date_val = date.today()
        if ocr_data.get("invoice_date"):
            try:
                # Parse YYYY-MM-DD from Gemini
                parts = ocr_data["invoice_date"].split('-')
                if len(parts) == 3:
                    inv_date_val = date(int(parts[0]), int(parts[1]), int(parts[2]))
            except: pass
            
        due_date_val = date.today()
        if ocr_data.get("due_date"):
            try:
                parts = ocr_data["due_date"].split('-')
                if len(parts) == 3:
                    due_date_val = date(int(parts[0]), int(parts[1]), int(parts[2]))
            except: pass

        invoice_date = st.date_input("Invoice Date", value=inv_date_val)
        due_date = st.date_input("Due Date", value=due_date_val)
        invoice_amount = st.number_input("Invoice Amount", min_value=0.0, step=0.01, value=float(ocr_data.get("invoice_amount") or 0.0))
        amount_paid = st.number_input("Amount Already Paid", min_value=0.0, step=0.01, value=float(ocr_data.get("amount_paid") or 0.0))
        
        submitted = st.form_submit_button("Save Invoice")
        
        if submitted:
            if not buyer_name or not invoice_number:
                st.error("Buyer Name and Invoice Number are required.")
            else:
                # Financial calculations using normal Python code
                balance_due = invoice_amount - amount_paid
                
                today = date.today()
                if balance_due <= 0:
                    status = "Paid"
                elif today > due_date:
                    status = "Overdue"
                elif amount_paid > 0:
                    status = "Partially paid"
                else:
                    status = "Due"
                    
                # Save to database
                try:
                    document_path = None
                    if uploaded_file is not None:
                        os.makedirs("uploads", exist_ok=True)
                        ext = os.path.splitext(uploaded_file.name)[1]
                        safe_invoice_num = "".join(c for c in invoice_number if c.isalnum() or c in ('-', '_'))
                        filename = f"{safe_invoice_num}_{int(datetime.now().timestamp())}{ext}"
                        filepath = os.path.join("uploads", filename)
                        
                        # We already have the file in memory, save it permanently
                        with open(filepath, "wb") as f:
                            f.write(uploaded_file.getvalue())
                            
                        document_path = filepath

                    conn = database.get_db_connection()
                    cursor = conn.cursor()
                    
                    # 1. Get or create buyer
                    cursor.execute("SELECT id FROM buyers WHERE buyer_name = ?", (buyer_name,))
                    buyer = cursor.fetchone()
                    
                    if buyer:
                        buyer_id = buyer['id']
                    else:
                        cursor.execute("INSERT INTO buyers (buyer_name) VALUES (?)", (buyer_name,))
                        buyer_id = cursor.lastrowid
                    
                    # 2. Insert invoice
                    cursor.execute('''
                        INSERT INTO invoices (
                            buyer_id, invoice_number, invoice_date, due_date, 
                            invoice_amount, amount_paid, balance_due, status, document_path
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        buyer_id, invoice_number, invoice_date, due_date,
                        invoice_amount, amount_paid, balance_due, status, document_path
                    ))
                    
                    conn.commit()
                    conn.close()
                    
                    st.success(f"Invoice **{invoice_number}** saved successfully!")
                    st.info(f"**Status:** {status} | **Balance Due:** ₹{balance_due:,.2f}")
                except Exception as e:
                    st.error(f"An error occurred while saving to the database: {e}")
