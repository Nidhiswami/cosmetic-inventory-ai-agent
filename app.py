import streamlit as st
import pandas as pd
import json

# -----------------------------
# Page Title & Sidebar
# -----------------------------
st.title("AI Supply Chain Assistant (Advanced Local Mode)")
st.write("Smart inventory monitoring system.")

st.sidebar.header("About Project")
st.sidebar.write("""
AI-powered cosmetic inventory management system.
Detects low stock items and provides structured JSON insights.
Built using Python, Pandas, and Streamlit.
""")

# -----------------------------
# Load Data Function
# -----------------------------
def load_data():
    try:
        df = pd.read_csv("inventory.csv")
        return df
    except Exception:
        st.error("Error loading inventory file.")
        return None


# -----------------------------
# Low Stock Logic
# -----------------------------
def get_low_stock(df):
    low_stock_df = df[df["Quantity"] < df["Reorder_Level"]].copy()
    if len(low_stock_df) > 0:
        low_stock_df["Reorder_Suggestion"] = (
            low_stock_df["Reorder_Level"] - low_stock_df["Quantity"]
        )
    return low_stock_df


# -----------------------------
# Total Inventory Logic
# -----------------------------
def get_inventory_summary(df):
    total_items = len(df)
    total_quantity = df["Quantity"].sum()
    return total_items, total_quantity


# -----------------------------
# Main Execution
# -----------------------------
df = load_data()

if df is not None:

    # 🔹 Data Validation
    required_columns = {"Item", "Quantity", "Reorder_Level"}
    if not required_columns.issubset(df.columns):
        st.error("CSV file is missing required columns.")
        st.stop()

    st.subheader("📦 Inventory Data")
    st.dataframe(df)

    # 🔹 Inventory Summary
    total_items, total_quantity = get_inventory_summary(df)

    st.subheader("📊 Inventory Summary")
    st.write(f"Total Items: {total_items}")
    st.write(f"Total Quantity in Stock: {total_quantity}")

    # 🔹 Low Stock Detection
    low_stock = get_low_stock(df)

    if len(low_stock) > 0:
        st.warning("🚨 Low Stock Alert!")
        st.dataframe(low_stock[["Item", "Quantity", "Reorder_Level"]])

    # 🔹 Reorder Suggestions
    st.subheader("📌 Reorder Suggestions")
    if len(low_stock) > 0:
        st.dataframe(low_stock[["Item", "Reorder_Suggestion"]])
        main_message = "Items below reorder level are listed."
    else:
        st.success("All items are sufficiently stocked!")
        main_message = "All items are sufficiently stocked!"

    # 🔹 Download Low Stock Report
    if len(low_stock) > 0:
        csv = low_stock.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Low Stock Report",
            data=csv,
            file_name="low_stock_report.csv",
            mime="text/csv"
        )

    # 🔹 Structured JSON Response
    response = {
        "low_stock_items": low_stock["Item"].tolist(),
        "total_low_stock_count": int(len(low_stock)),
        "message": main_message
    }

    st.subheader("🤖 AI Response (Structured JSON)")
    st.json(response)

    # 🔹 Bar Chart
    st.subheader("📈 Stock Levels")
    st.bar_chart(df.set_index("Item")["Quantity"])

    # 🔹 Question Section
    user_input = st.text_input("Enter your question:")

    if user_input:
        user_input = user_input.lower()

        if "low" in user_input:
            result = response

        elif "total" in user_input:
            result = {
                "total_items": int(total_items),
                "total_quantity": int(total_quantity),
                "message": "Overall inventory summary."
            }

        elif "summary" in user_input:
            result = {
                "total_items": int(total_items),
                "low_stock_count": int(len(low_stock)),
                "message": "Inventory summary overview."
            }

        elif "high" in user_input or "sufficient" in user_input or "good" in user_input:
            if len(low_stock) > 0:
                result = {
                    "message": "Stock is NOT sufficient. Some items are below reorder level."
                }
            else:
                result = {
                    "message": "Stock levels are good. All items are sufficiently stocked."
                }

        else:
            result = {
                "message": "Sorry, I can answer about low stock, total stock, summary, or stock status."
            }

        st.write("### AI Response (Structured JSON)")
        st.code(json.dumps(result, indent=2), language="json")