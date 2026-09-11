# Settl

**Payment recovery and invoice tracking for small businesses.**

Settl helps small contractors, suppliers, and service providers organize unpaid invoices, track partial payments, calculate overdue balances, and generate professional payment reminders — without needing accounting expertise or paid software.

Built as part of the FFE Tech Entrepreneurship Program 2026.

---

## The Problem

Small businesses that sell on credit — electricians, fabricators, printers, contractors, wholesalers — often lose track of:

- Which invoices are overdue and by how much.
- How much a buyer still owes after partial payments.
- What documents exist as proof (invoice, work order, delivery proof).
- When and how they last followed up with a buyer.

This usually lives across notebooks, WhatsApp chats, and memory — not a system. Delayed payments create real cash-flow pressure, and following up is tedious enough that it often just doesn't happen.

## What Settl Does

Settl is **not** a legal-advice tool and does not file cases or guarantee recovery. It is a payment-tracking and communication assistant that:

- Extracts invoice details from uploaded PDFs/images using OCR.
- Lets the user confirm or correct extracted fields before saving.
- Tracks full and partial payments against each invoice.
- Calculates outstanding balance and overdue days automatically (never via AI).
- Generates friendly, firm, and escalation-stage reminder drafts in English and Telugu.
- Produces a document checklist and PDF follow-up report per invoice.
- Shows a dashboard of total outstanding, total overdue, and invoices due soon.

## Product Principles

- **AI extracts and drafts. Code calculates.** All financial math (balances, overdue days, status) is deterministic Python — never left to an LLM.
- **Nothing saves without confirmation.** OCR and AI-extracted fields are always shown to the user for review before being written to the database.
- **No legal claims.** Settl prepares documentation and communication; it explicitly avoids presenting itself as legal advice or a guarantee of payment recovery.

## Tech Stack

| Layer | Tool |
|---|---|
| Frontend/UI | Streamlit |
| Backend logic | Python |
| Database | SQLite |
| OCR | Tesseract (pytesseract) |
| AI extraction & drafting | Gemini API (free tier) |
| PDF reports | ReportLab |
| Deployment | Streamlit Community Cloud |

All tools used are free at the prototype stage — no paid APIs required.

## Project Structure

```
settl/
│
├── app.py                # Main Streamlit app (dashboard + add invoice)
├── database.py           # SQLite schema and queries
├── calculations.py       # Balance, overdue, and status logic
├── reminders.py          # Reminder templates (English/Telugu)
├── ocr_service.py        # Tesseract text extraction
├── ai_service.py         # Gemini structured extraction and drafting
├── pdf_reports.py        # PDF report generation
├── requirements.txt
├── .env                  # API keys (not committed)
├── .gitignore
│
├── data/
│   └── app.db             # SQLite database (not committed)
│
└── uploads/                # Uploaded invoice files (not committed)
```

## Getting Started

### 1. Clone and set up the environment

```bash
git clone https://github.com/<your-username>/settl.git
cd settl
python -m venv .venv
```

Activate the environment:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# Windows Command Prompt
.venv\Scripts\activate.bat

# macOS/Linux
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Tesseract OCR

**Windows:**
```bash
winget install -e --id UB-Mannheim.TesseractOCR
```

Verify installation:
```bash
tesseract --version
```

If not recognized, add `C:\Program Files\Tesseract-OCR` to your system PATH.

### 4. Set up environment variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_google_ai_studio_api_key_here
```

Get a free API key from [Google AI Studio](https://aistudio.google.com) — no credit card required.

### 5. Run the app

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.

## Core Workflow

1. **Add a buyer** — name, contact, payment terms.
2. **Add an invoice** — manually, or upload a PDF/image for OCR extraction.
3. **Confirm extracted details** — edit any field OCR/AI got wrong before saving.
4. **Record payments** — full or partial, with date and reference.
5. **Monitor the dashboard** — total outstanding, overdue count, due-this-week.
6. **Generate a reminder** — copy, download as PDF, or mark as sent.
7. **Prepare documentation** — use the checklist for follow-up or escalation.

## Current Status

This is an early-stage MVP built for validation, not production use. Known limitations:

- OCR accuracy varies with image quality and invoice layout.
- No WhatsApp/SMS/email sending — reminders are copy-paste or PDF export only.
- Single-user, no authentication layer yet.
- Demo data only; do not upload real confidential business documents to the public deployment.

## Roadmap

- [ ] Voice-based payment entry (Telugu/English)
- [ ] WhatsApp-ready one-click reminder sending
- [ ] Multi-business / multi-user accounts
- [ ] Buyer-level risk scoring based on payment history
- [ ] Export to accounting formats (Tally, Excel)

## Disclaimer

Settl is a documentation and communication assistant. It does not provide legal advice, does not guarantee payment recovery, and does not determine legal eligibility for any government scheme or delayed-payment mechanism. Users should consult a qualified professional for legal or financial advice.

## Acknowledgements

Built as part of the FFE Tie Entrepreneurship Program 2026, under the guidance of Prof. Raj Jaswa, Prof. Milind Kopikar, and the FFE mentor team.
