💸 BudgetPulse

A cloud-connected personal expense tracking and budgeting application
built with Python, Streamlit, Pandas, and Supabase.

BudgetPulse is a responsive web-based expense manager that lets users
securely log in, record and manage expenses, track recurring
subscriptions, analyze spending, set a monthly budget, switch between
supported currencies, and back up/restore expense data using CSV files.

✨ Features

🔐 Authentication

User registration with email and password

User login using Supabase Authentication

Logout functionality

User-specific session state

➕ Expense Management

Add new expenses with:

Date

Amount

Category

Description

View saved expenses in a table

Update existing expenses

Delete existing expenses

🔄 Recurring Subscriptions

Add recurring bills/subscriptions

Store subscription name, amount, and category

Automatically inject recurring expenses for the current month

Remove subscriptions when they are no longer needed

🔍 Expense Filtering

Filter expenses by date range

Filter by one or more categories

Display filtered expense records in a tabular view

🧠 Spending Insights

Calculate total spending

Identify the highest-spending category

Display category-wise spending using a bar chart

Display monthly spending trends using a line chart

🎯 Budget Tracker

Set a monthly spending budget

Track current-month spending

Calculate remaining budget

Display budget utilization with a progress bar

🌐 Multi-Currency Support

BudgetPulse stores monetary values in INR as its base currency and
provides conversion/display support for:

₹ INR

$ USD

€ EUR

£ GBP

¥ JPY

د.إ AED

The exchange rates currently used by the application are predefined in
the source code and are not fetched from a live exchange-rate API.

📂 CSV Upload & Download

Upload previous expense data from a CSV file

Import uploaded records into the user's cloud account

Download stored expense data as CSV

Useful for cloud backup and restoring previous records

📱 Responsive Interface

Wide desktop layout

Responsive CSS for smaller screens

Mobile-friendly buttons and columns

🛠️ Tech Stack

Technology          Purpose

Python          Application logic
Streamlit       Web application UI
Pandas          Data processing, filtering, grouping, and analysis
Supabase        Authentication and cloud database
Supabase Auth   User registration and login
CSV             Data import/export

The project's dependency file contains:

streamlit
pandas
supabase

🏗️ Application Architecture

                    ┌─────────────────────┐
                    │      User           │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Streamlit UI      │
                    │    BudgetPulse      │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
        Authentication    Expense Logic    Analytics
              │                │                │
              └────────────────┼────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      Supabase       │
                    │ Auth + PostgreSQL   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Expenses /          │
                    │ Subscriptions      │
                    └─────────────────────┘

📁 Project Structure

A simple GitHub structure for the project:

BudgetPulse/
│
├── expenses.py
├── requirements.txt
├── README.md
└── .streamlit/
    └── secrets.toml

File descriptions

expenses.py --- Main Streamlit application.

requirements.txt --- Python dependencies.

README.md --- Project documentation.

.streamlit/secrets.toml --- Local Supabase credentials. Do not
upload this file to GitHub.

🚀 Getting Started

1. Clone the repository

git clone https://github.com/YOUR-USERNAME/BudgetPulse.git
cd BudgetPulse

2. Create a virtual environment

python -m venv venv

Activate it:

macOS / Linux

source venv/bin/activate

Windows

venv\Scripts\activate

3. Install dependencies

pip install -r requirements.txt

☁️ Supabase Configuration

BudgetPulse uses Supabase for authentication and cloud data storage.

The application reads the following values from Streamlit secrets:

SUPABASE_URL = "your-supabase-project-url"
SUPABASE_KEY = "your-supabase-key"

Create the following file locally:

.streamlit/secrets.toml

Example:

SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-supabase-key"

⚠️ Security

Never commit your real Supabase credentials to GitHub.

Add this to .gitignore:

.streamlit/secrets.toml
venv/
__pycache__/
*.pyc
.DS_Store

🗄️ Database Requirements

The application expects two Supabase tables:

expenses

The application uses these fields:

Field           Purpose

id            Expense record identifier
user_id       User associated with the expense
date          Expense date
amount        Expense amount stored in INR
category      Expense category
description   Expense description

subscriptions

The application uses these fields:

Field           Purpose

id            Subscription identifier
user_id       User associated with the subscription
amount        Recurring amount stored in INR
category      Subscription category
description   Subscription/bill name

Configure appropriate Supabase authentication and database access
policies for production use. The application code associates inserted
records with the currently authenticated user's ID.

▶️ Run the Application

Start BudgetPulse with:

streamlit run expenses.py

Streamlit will provide a local URL where you can open the application in
your browser.

🧭 Application Navigation

After logging in, the sidebar provides these sections:

➕ Add Expense
✏️ Update/Delete
🔄 Subscriptions
🔍 Filter Data
🧠 Insights
🎯 Budget Tracker
📂 Upload / Download

Add Expense

Enter the expense date, amount, category, and description, then save the
record to Supabase.

Update/Delete

Select an existing record and either update its information or delete
it.

Subscriptions

Create recurring bills that BudgetPulse can automatically add to the
current month's expenses.

Filter Data

Select a date range and categories to inspect a subset of expenses.

Insights

View total spending, the top spending category, category breakdown, and
monthly spending trends.

Budget Tracker

Set a monthly budget and monitor how much has been spent and how much
remains.

Upload / Download

Import expense records from CSV or export the cloud expense data as a
CSV file.

📄 CSV Import Format

For uploading previous expense records, the application expects these
column names:

Date
Amount
Category
Description

Example:

Date,Amount,Category,Description
2026-09-01,500,Food,Lunch
2026-09-02,1200,Travel,Cab
2026-09-03,800,Shopping,Clothes

The uploaded Amount is treated as the base INR amount by the
application.

💱 Currency Handling

BudgetPulse uses INR as its internal base currency.

When a user selects another supported currency:

Stored INR amount
        │
        ▼
Currency conversion
        │
        ▼
Selected display currency

When an expense is entered in the selected currency, the application
converts it back to INR before storing it in Supabase.

This keeps the database values normalized around a single base currency.

🔄 Automatic Subscription Logic

BudgetPulse checks the user's saved subscriptions when the application
session initializes.

For each subscription, it checks whether the corresponding recurring
expense already exists for the current month.

If it does not exist, BudgetPulse creates an expense entry dated on the
first day of the current month.

This helps prevent the same recurring bill from being automatically
inserted multiple times during the same session/month.

📊 Expense Categories

The application supports these expense categories:

Food
Travel
Shopping
Bills
Health
Other

Subscriptions use the same categories, with Bills appearing first in
the subscription form.

🔒 Data & Security Notes

Authentication is handled through Supabase Auth.

Supabase credentials are loaded through Streamlit secrets.

Expense and subscription records include a user_id.

Keep your Supabase credentials outside the public repository.

Configure appropriate Row Level Security (RLS) policies in Supabase
before deploying the application for real users.

🌱 Possible Future Improvements

These are potential extensions rather than features currently
implemented in the uploaded source code:

Live currency exchange-rate API

Persistent monthly budgets in the database

Advanced charts and dashboards

Expense search by description

Custom expense categories

Recurring subscription frequency options

Financial reports

Export to additional formats

More granular Supabase Row Level Security policies

👨‍💻 Project

Project Name: BudgetPulse

Type: Personal Expense & Budget Management Web Application

Built With: Python • Streamlit • Pandas • Supabase

⭐ GitHub

If you find this project useful, consider giving the repository a ⭐.
