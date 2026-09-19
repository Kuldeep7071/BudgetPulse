import streamlit as st
import pandas as pd
from datetime import date
from supabase import create_client, Client

# 1. Page Configuration & Responsive CSS
st.set_page_config(page_title="Smart Expense Tracker Pro", layout="wide", page_icon="💸")

st.markdown("""
<style>
    .block-container { padding: 2rem 1.5rem; }
    @media (max-width: 768px) {
        .block-container { padding: 1rem 0.8rem; }
        [data-testid="column"] { width: 100% !important; min-width: 100% !important; margin-bottom: 0.5rem; }
        .stButton > button { width: 100% !important; }
    }
</style>
""", unsafe_allow_html=True)

# 2. Initialize Supabase
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

# 3. Authentication State
if "user" not in st.session_state:
    st.session_state.user = None

# 4. Currency Conversion Rates (Base: INR)
RATES_FROM_INR = {
    "₹ INR": {"rate": 1.0, "symbol": "₹"},
    "$ USD": {"rate": 0.012, "symbol": "$"},
    "€ EUR": {"rate": 0.011, "symbol": "€"},
    "£ GBP": {"rate": 0.0095, "symbol": "£"},
    "¥ JPY": {"rate": 1.85, "symbol": "¥"},
    "د.إ AED": {"rate": 0.044, "symbol": "AED "}
}

# -------------------------------------------------------------
# LOGIN & REGISTRATION SYSTEM
# -------------------------------------------------------------
if not st.session_state.user:
    st.title("🔐 Login to BudgetPulse")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login", type="primary"):
            try:
                response = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state.user = response.user
                st.rerun()
            except Exception as e:
                st.error("Login failed. Check your credentials.")
                
    with tab2:
        new_email = st.text_input("Email", key="reg_email")
        new_password = st.text_input("Password", type="password", key="reg_pass")
        if st.button("Sign Up"):
            try:
                supabase.auth.sign_up({"email": new_email, "password": new_password})
                st.success("Registration successful! You can now log in.")
            except Exception as e:
                st.error("Registration failed. Please try again.")
                
    st.stop()

# -------------------------------------------------------------
# DATABASE FETCH HELPERS
# -------------------------------------------------------------
def fetch_expenses():
    response = supabase.table("expenses").select("*").execute()
    if response.data:
        df = pd.DataFrame(response.data)
        df["date"] = pd.to_datetime(df["date"])
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
        return df
    return pd.DataFrame(columns=["id", "date", "amount", "category", "description"])

def fetch_subs():
    response = supabase.table("subscriptions").select("*").execute()
    if response.data:
        df = pd.DataFrame(response.data)
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
        return df
    return pd.DataFrame(columns=["id", "amount", "category", "description"])

# -------------------------------------------------------------
# AUTO-INJECT SUBSCRIPTIONS
# -------------------------------------------------------------
def auto_inject_subscriptions():
    subs_df = fetch_subs()
    if subs_df.empty:
        return
        
    expenses_df = fetch_expenses()
    today = date.today()
    first_of_month = today.replace(day=1)
    
    if not expenses_df.empty:
        this_month = expenses_df[(expenses_df["date"].dt.month == today.month) & (expenses_df["date"].dt.year == today.year)]
    else:
        this_month = pd.DataFrame(columns=["description"])
        
    new_entries = []
    for _, sub in subs_df.iterrows():
        expected_desc = f"🔄 {sub['description']}"
        if this_month.empty or this_month[this_month["description"] == expected_desc].empty:
            new_entries.append({
                "user_id": st.session_state.user.id,
                "date": str(first_of_month),
                "amount": float(sub["amount"]), # Inserted in base currency
                "category": sub["category"],
                "description": expected_desc
            })
            
    if new_entries:
        supabase.table("expenses").insert(new_entries).execute()
        st.toast(f"✅ Auto-injected {len(new_entries)} recurring bills for this month!")

if "subs_checked" not in st.session_state:
    auto_inject_subscriptions()
    st.session_state.subs_checked = True

df = fetch_expenses()

# -------------------------------------------------------------
# SIDEBAR & CURRENCY ENGINE
# -------------------------------------------------------------
st.sidebar.success(f"👤 {st.session_state.user.email}")

currency_choice = st.sidebar.selectbox("🌐 Active Currency", list(RATES_FROM_INR.keys()), index=0)
active_rate = RATES_FROM_INR[currency_choice]["rate"]
active_sym = RATES_FROM_INR[currency_choice]["symbol"]

def to_active(val_inr): return val_inr * active_rate
def to_inr(val_active): return val_active / active_rate

st.sidebar.divider()
menu = st.sidebar.radio("📌 Navigation", [
    "➕ Add Expense",
    "✏️ Update/Delete",
    "🔄 Subscriptions",
    "🔍 Filter Data",
    "🧠 Insights",
    "🎯 Budget Tracker",
    "📂 Upload / Download"
])

if st.sidebar.button("Logout"):
    supabase.auth.sign_out()
    st.session_state.clear()
    st.rerun()

st.title("💸 Smart Expense Tracker Pro")

# -------------------------------------------------------------
# 1. ADD EXPENSE
# -------------------------------------------------------------
if menu == "➕ Add Expense":
    st.subheader("➕ Add New Expense")
    with st.form("add_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            date_input = st.date_input("Date")
            amount_input = st.number_input(f"Amount ({active_sym})", min_value=0.0)
        with col2:
            category = st.selectbox("Category", ["Food", "Travel", "Shopping", "Bills", "Health", "Other"])
            description = st.text_input("Description")

        if st.form_submit_button("Save Expense"):
            supabase.table("expenses").insert({
                "user_id": st.session_state.user.id,
                "date": str(date_input),
                "amount": to_inr(amount_input), # Save in base currency
                "category": category,
                "description": description
            }).execute()
            st.success("Added to database!")
            st.rerun()

    if not df.empty:
        df_display = df.copy()
        df_display["date"] = df_display["date"].dt.date
        df_display[f"Amount ({active_sym})"] = df_display["amount"].apply(to_active).round(2)
        st.dataframe(df_display[["date", f"Amount ({active_sym})", "category", "description"]], width="stretch")

# -------------------------------------------------------------
# 2. UPDATE / DELETE
# -------------------------------------------------------------
elif menu == "✏️ Update/Delete":
    st.subheader("✏️ Manage Existing Entries")
    if df.empty:
        st.warning("No data available.")
    else:
        if "selected_index" not in st.session_state:
            st.session_state.selected_index = None

        st.write("### Select a row to edit")
        
        df_editor = df.copy()
        df_editor["date"] = df_editor["date"].dt.date
        df_editor[f"Amount ({active_sym})"] = df_editor["amount"].apply(to_active).round(2)
        df_editor.insert(0, "Select", False)

        if st.session_state.selected_index is not None and st.session_state.selected_index < len(df_editor):
            df_editor.at[st.session_state.selected_index, "Select"] = True

        def handle_select():
            changes = st.session_state.editor.get("edited_rows", {})
            for idx, val in changes.items():
                if val.get("Select"):
                    st.session_state.selected_index = int(idx)

        st.data_editor(
            df_editor[["Select", "date", f"Amount ({active_sym})", "category", "description"]],
            key="editor",
            on_change=handle_select,
            disabled=["date", f"Amount ({active_sym})", "category", "description"],
            width="stretch"
        )

        if st.session_state.selected_index is not None:
            row = df.loc[st.session_state.selected_index]
            db_id = row["id"]
            
            st.write("### Edit Entry")
            col1, col2 = st.columns(2)
            with col1:
                edit_date = st.date_input("Edit Date", row["date"].date())
                current_converted = float(to_active(row["amount"]))
                edit_amount = st.number_input(f"Edit Amount ({active_sym})", value=current_converted)
            with col2:
                cat_options = ["Food", "Travel", "Shopping", "Bills", "Health", "Other"]
                cat_idx = cat_options.index(row["category"]) if row["category"] in cat_options else 0
                edit_cat = st.selectbox("Category", cat_options, index=cat_idx)
                edit_desc = st.text_input("Description", row["description"])

            c1, c2 = st.columns(2)
            if c1.button("Update Entry"):
                supabase.table("expenses").update({
                    "date": str(edit_date),
                    "amount": to_inr(edit_amount),
                    "category": edit_cat,
                    "description": edit_desc
                }).eq("id", db_id).execute()
                st.session_state.selected_index = None
                st.rerun()

            if c2.button("Delete Entry"):
                supabase.table("expenses").delete().eq("id", db_id).execute()
                st.session_state.selected_index = None
                st.rerun()

# -------------------------------------------------------------
# 3. SUBSCRIPTIONS
# -------------------------------------------------------------
elif menu == "🔄 Subscriptions":
    st.subheader("🔄 Manage Recurring Bills")
    st.caption("These will automatically be added to your expenses on the 1st of every month.")

    subs_df = fetch_subs()

    with st.form("add_sub_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            sub_desc = st.text_input("Bill Name (e.g., Netflix)")
        with c2:
            sub_amount = st.number_input(f"Amount ({active_sym})", min_value=0.0)
        with c3:
            sub_cat = st.selectbox("Category", ["Bills", "Health", "Shopping", "Food", "Travel", "Other"])
        
        if st.form_submit_button("Add Recurring Bill"):
            if sub_desc:
                supabase.table("subscriptions").insert({
                    "user_id": st.session_state.user.id,
                    "amount": to_inr(sub_amount),
                    "category": sub_cat,
                    "description": sub_desc
                }).execute()
                st.success(f"{sub_desc} added successfully!")
                st.rerun()

    if not subs_df.empty:
        st.write("### Active Subscriptions")
        for idx, row in subs_df.iterrows():
            col1, col2, col3 = st.columns([3, 1, 1])
            col1.write(f"**{row['description']}** ({row['category']})")
            col2.write(f"{active_sym}{to_active(row['amount']):,.2f}")
            if col3.button("❌ Remove", key=f"del_sub_{row['id']}"):
                supabase.table("subscriptions").delete().eq("id", row["id"]).execute()
                st.rerun()

# -------------------------------------------------------------
# 4. FILTER DATA
# -------------------------------------------------------------
elif menu == "🔍 Filter Data":
    st.subheader("🔍 Filter Your Expenses")
    if df.empty:
        st.warning("No data available.")
    else:
        c1, c2 = st.columns(2)
        start = pd.to_datetime(c1.date_input("Start Date", df["date"].min().date()))
        end = pd.to_datetime(c2.date_input("End Date", df["date"].max().date()))

        categories = st.multiselect("Category", df["category"].unique(), default=df["category"].unique())
        filtered = df[(df["date"] >= start) & (df["date"] <= end) & (df["category"].isin(categories))].copy()

        filtered["date"] = filtered["date"].dt.date
        filtered[f"Amount ({active_sym})"] = filtered["amount"].apply(to_active).round(2)
        st.dataframe(filtered[["date", f"Amount ({active_sym})", "category", "description"]], width="stretch")

# -------------------------------------------------------------
# 5. INSIGHTS
# -------------------------------------------------------------
elif menu == "🧠 Insights":
    st.subheader("🧠 Smart Insights")
    if df.empty:
        st.warning("No data available.")
    else:
        df["ConvertedAmount"] = df["amount"].apply(to_active)
        total = df["ConvertedAmount"].sum()
        cat_spend = df.groupby("category")["ConvertedAmount"].sum()
        
        c1, c2 = st.columns(2)
        c1.metric(f"💸 Total Spend", f"{active_sym} {total:,.2f}")
        c2.metric("🏆 Top Category", cat_spend.idxmax() if not cat_spend.empty else 'N/A')

        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"### Category Breakdown ({active_sym})")
            st.bar_chart(cat_spend)
        with col2:
            st.write(f"### Monthly Trend ({active_sym})")
            df["Month"] = df["date"].dt.to_period("M").astype(str)
            monthly = df.groupby("Month")["ConvertedAmount"].sum()
            st.line_chart(monthly)

# -------------------------------------------------------------
# 6. BUDGET TRACKER
# -------------------------------------------------------------
elif menu == "🎯 Budget Tracker":
    st.subheader("🎯 Monthly Budget Tracker")
    
    if "monthly_budget_inr" not in st.session_state:
        st.session_state.monthly_budget_inr = 25000.0

    current_budget_active = to_active(st.session_state.monthly_budget_inr)
    new_budget_active = st.number_input(
        f"Set Monthly Budget limit ({active_sym})", 
        value=float(round(current_budget_active, 2)), step=500.0
    )
    st.session_state.monthly_budget_inr = to_inr(new_budget_active)

    today = date.today()
    if not df.empty:
        current = df[(df["date"].dt.month == today.month) & (df["date"].dt.year == today.year)]
        spent_inr = current["amount"].sum()
    else:
        spent_inr = 0.0

    spent_active = to_active(spent_inr)
    remaining_active = new_budget_active - spent_active

    pct_used = min(1.0, spent_active / new_budget_active) if new_budget_active > 0 else 0.0
    st.progress(pct_used)
    
    b1, b2 = st.columns(2)
    b1.metric("Spent This Month", f"{active_sym}{spent_active:,.2f}")
    b2.metric("Remaining", f"{active_sym}{remaining_active:,.2f}", delta=f"{active_sym}{remaining_active:,.2f}")

# -------------------------------------------------------------
# 7. UPLOAD / DOWNLOAD
# -------------------------------------------------------------
elif menu == "📂 Upload / Download":
    st.subheader("📂 Cloud Backup & Restore")
    
    file = st.file_uploader("Upload previous CSV data to your cloud account", type=["csv"])
    if file:
        uploaded = pd.read_csv(file)
        records = []
        for _, row in uploaded.iterrows():
            records.append({
                "user_id": st.session_state.user.id,
                "date": str(pd.to_datetime(row["Date"]).date()),
                "amount": float(row["Amount"]), # Assumes uploaded CSV is in base INR
                "category": row["Category"],
                "description": row["Description"]
            })
            
        if records:
            supabase.table("expenses").insert(records).execute()
            st.success(f"Successfully uploaded {len(records)} records to the cloud!")
            st.rerun()

    if not df.empty:
        csv_export = df[["date", "amount", "category", "description"]].copy()
        csv_export = csv_export.rename(columns={"date": "Date", "amount": "Amount (INR)", "category": "Category", "description": "Description"})
        st.download_button("Download Cloud Data as CSV", csv_export.to_csv(index=False), "my_cloud_expenses.csv")