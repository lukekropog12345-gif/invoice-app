# InvoiceFlow — Python Invoice Generator

A clean, professional invoice generator built with Python (Flask) and ReportLab.
Generates real downloadable PDF invoices.

---

## Setup (First Time Only)

### 1. Make sure Python is installed
Open Terminal (Mac/Linux) or Command Prompt (Windows) and type:
```
python --version
```
You should see Python 3.x.x. If not, download it at https://python.org

### 2. Install the required libraries
In your terminal, navigate to this folder and run:
```
pip install -r requirements.txt
```

---

## Running the App

```
python app.py
```

Then open your browser and go to:
**http://localhost:5000**

That's it! Fill in your invoice details and click "Download PDF Invoice".

---

## How to Stop the App
Press `Ctrl + C` in the terminal.

---

## File Structure
```
invoice_app/
├── app.py              ← The main Python server
├── requirements.txt    ← Libraries needed
├── README.md           ← This file
└── templates/
    └── index.html      ← The web interface
```

---

## Going Online (Getting Paid Customers)

To put this on the internet so others can use it:

### Free option: Railway.app
1. Create a free account at https://railway.app
2. Upload this folder
3. They give you a live URL — share it with clients!

### Add payments later (Stripe)
Once you have users, add Stripe ($10-20/month subscriptions).
Ask Claude to help you add Stripe payments when you're ready!

---

## Ideas to Grow This App
- Add user accounts so each business saves their info
- Let clients pay invoices directly online (Stripe)
- Send invoices by email automatically
- Add a dashboard to track paid/unpaid invoices
- Custom branding / logo upload

Good luck! 🚀
