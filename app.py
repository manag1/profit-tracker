import streamlit as st
import pandas as pd
import os

FILE_PATH = "profit_data.csv"

# Load or create CSV
def load_data():
    if os.path.exists(FILE_PATH):
        return pd.read_csv(FILE_PATH, parse_dates=["Date"])
    else:
        return pd.DataFrame(columns=["Date", "DayProfitLoss", "ProfitDistributed"])

def save_data(df):
    df.to_csv(FILE_PATH, index=False)

# Initial Setup
st.set_page_config(page_title="Profit Tracker", layout="wide")
st.title("📈 Profit Distribution Tracker")

# Load data
data = load_data()

# --- Input Form ---
st.subheader("➕ Enter Today's Record")
with st.form("entry_form"):
    date = st.date_input("Date")
    day_pl = st.number_input("Day's Profit/Loss", step=1.0, format="%.2f")
    dist_profit = st.number_input("Distributed Profit", step=1.0, format="%.2f")
    submit = st.form_submit_button("Submit")

# Handle submission
if submit:
    new_entry = pd.DataFrame([{
        "Date": pd.to_datetime(date),
        "DayProfitLoss": day_pl,
        "ProfitDistributed": dist_profit
    }])
    data = pd.concat([data, new_entry], ignore_index=True)
    save_data(data)
    st.success("✅ Record saved!")
    st.rerun()

# --- Delete Records ---
if not data.empty:
    st.subheader("🗑️ Delete Old Records")
    data_sorted = data.sort_values(by="Date", ascending=False).reset_index(drop=True)
    data_sorted["Delete"] = False

    for i in range(len(data_sorted)):
        data_sorted.at[i, "Delete"] = st.checkbox(
            f"{data_sorted.at[i, 'Date'].strftime('%d-%b-%Y')} | P/L: {data_sorted.at[i, 'DayProfitLoss']}, Dist: {data_sorted.at[i, 'ProfitDistributed']}",
            key=f"del_{i}"
        )

    if st.button("Delete Selected"):
        data = data_sorted[~data_sorted["Delete"]].drop(columns=["Delete"]).reset_index(drop=True)
        save_data(data)
        st.success("🗑️ Deleted selected rows.")
        st.rerun()

# --- Calculations ---
if not data.empty:
    st.subheader("📊 Summary & Calculations")

    # Total Calculations
    total_day_pl = data["DayProfitLoss"].sum()
    total_dist_profit = data["ProfitDistributed"].sum()
    cumulative_loss = total_day_pl - total_dist_profit
    net_profit =  (total_dist_profit - cumulative_loss)
    each_person_total = total_dist_profit / 3 if total_dist_profit else 0

    # Latest Entry
    latest = data.sort_values(by="Date", ascending=False).iloc[0]
    latest_adjusted = latest["DayProfitLoss"] - latest["ProfitDistributed"] if latest["ProfitDistributed"] > 0 else 0
    each_person_day = latest["ProfitDistributed"] / 3 if latest["ProfitDistributed"] else 0

    # col1, col2, col3 = st.columns(3)

    # Show
    st.metric("Cumulative Loss", f"{cumulative_loss:.2f}")
    st.metric("Day Profit/Loss", f"{latest['DayProfitLoss']:.2f}")
    st.metric("Adjusted for Cumulative Loss", f"{latest_adjusted:.2f}")
    st.metric("Each Person Day Profit", f"{each_person_day:.2f}")
    st.metric("Each Person Total Profit", f"{each_person_total:.2f}")
    st.metric("Total Distributed Profit", f"{total_dist_profit:.2f}")
    st.metric("Net Profit", f"{net_profit:.2f}")

    # --- Formatted Business Statement ---
    st.write("### 🧾 Copyable Business Statement")

    statement = f"""*Futures Business statement*(nifty)  
Cumulative loss {cumulative_loss:.0f}  
Day Loss {latest['DayProfitLoss']:.0f}  
Adjusted for cum loss {latest_adjusted:.0f}  
Profit distributed {latest['ProfitDistributed']:.0f}  
Each person day profit {each_person_day:.0f}  
Each person total profit {each_person_total:.0f}  
Distributed Profit {total_dist_profit:.0f}  
Net Profit {net_profit:.0f}
    """

    # Display in a text area for manual copy (mobile-friendly)
    st.text_area("📋 Copy this message", value=statement, height=220)

    # Optional: Add a copy button using JS for web (works on desktop browsers)
    st.markdown("""
        <button onclick="navigator.clipboard.writeText(document.getElementById('copyMe').innerText)"
        style="background-color:#4CAF50;border:none;color:white;padding:10px 24px;
        text-align:center;text-decoration:none;display:inline-block;font-size:16px;
        margin:4px 2px;border-radius:8px;cursor:pointer;">📄 Copy to Clipboard</button>

        <pre id="copyMe" style="display:none;">""" + statement + """</pre>
    """, unsafe_allow_html=True)

    import urllib.parse

    # --- WhatsApp Web Sharing ---
    st.write("### 📤 Send to WhatsApp")

    # WhatsApp number: add your number here (with country code, no + or spaces)
    whatsapp_number = "918919522413"  # replace with your number

    # Encode message
    encoded_message = urllib.parse.quote(statement)

    # Create WhatsApp link
    whatsapp_link = f"https://wa.me/{whatsapp_number}?text={encoded_message}"

    # Display clickable button
    st.markdown(
        f"""
        <a href="{whatsapp_link}" target="_blank">
            <button style="background-color:#25D366;color:white;padding:10px 20px;
            border:none;border-radius:8px;font-size:16px;cursor:pointer;">
            📲 Send to WhatsApp
            </button>
        </a>
        """,
        unsafe_allow_html=True
    )
    # Data Table
    st.write("### 📋 Full Data Table")
    st.dataframe(data.sort_values(by="Date", ascending=False), use_container_width=True)
else:
    st.info("No records yet. Please enter data.")
