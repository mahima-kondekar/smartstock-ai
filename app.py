import math
import os

import pandas as pd
import streamlit as st

# MySQL is optional. The app also works without it.
try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="SmartStock AI",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --------------------------------------------------
# DEMO INVENTORY DATA
# These are fictional sample records.
# --------------------------------------------------

DEFAULT_DATA = [
    ["P101", "Wireless Mouse", "Accessories", 18, 20, 5, 4, 450],
    ["P102", "Bluetooth Headphones", "Electronics", 65, 20, 4, 5, 1200],
    ["P103", "USB-C Charger", "Accessories", 8, 15, 6, 3, 350],
    ["P104", "Mechanical Keyboard", "Electronics", 12, 18, 3, 6, 1800],
    ["P105", "Laptop Stand", "Accessories", 42, 15, 2, 4, 700],
    ["P106", "Power Bank", "Electronics", 6, 12, 4, 5, 900],
    ["P107", "USB Cable", "Accessories", 120, 25, 8, 3, 120],
    ["P108", "Webcam", "Electronics", 25, 15, 2, 5, 1500],
    ["P109", "SSD 1TB", "Storage", 9, 12, 2, 7, 4200],
    ["P110", "Monitor", "Electronics", 30, 10, 2, 6, 6500],
    ["P111", "Phone Case", "Accessories", 80, 20, 5, 3, 180],
    ["P112", "Router", "Networking", 14, 15, 3, 5, 1100],
]

COLUMNS = [
    "product_id",
    "product_name",
    "category",
    "stock",
    "safety_stock",
    "daily_demand",
    "lead_time",
    "cost_price"
]


# --------------------------------------------------
# INVENTORY ANALYSIS
# --------------------------------------------------

def analyse_inventory(data):

    df = data.copy()

    numeric_columns = [
        "stock",
        "safety_stock",
        "daily_demand",
        "lead_time",
        "cost_price"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df = df.dropna(subset=COLUMNS).copy()

    df["days_remaining"] = df.apply(
        lambda row: (
            math.floor(row["stock"] / row["daily_demand"])
            if row["daily_demand"] > 0 else 999
        ),
        axis=1
    )

    df["reorder_point"] = (
        df["daily_demand"] * df["lead_time"]
        + df["safety_stock"]
    )

    df["reorder_qty"] = (
        df["reorder_point"] - df["stock"]
    ).clip(lower=0)

    def get_status(row):

        if row["stock"] <= 0:
            return "Out of Stock"

        elif row["days_remaining"] <= row["lead_time"]:
            return "Critical"

        elif row["stock"] <= row["reorder_point"]:
            return "Reorder Soon"

        return "Healthy"

    df["status"] = df.apply(get_status, axis=1)

    df["inventory_value"] = (
        df["stock"] * df["cost_price"]
    )

    return df


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

def get_demo_data():
    return pd.DataFrame(DEFAULT_DATA, columns=COLUMNS)


if "inventory_data" not in st.session_state:
    st.session_state.inventory_data = get_demo_data()


if "data_source" not in st.session_state:
    st.session_state.data_source = "Demo data"


# --------------------------------------------------
# DARK THEME DESIGN
# --------------------------------------------------

st.markdown("""
<style>

.stApp {
    background-color: #080D18;
    color: #E5EAF3;
}

[data-testid="stSidebar"] {
    background-color: #101827;
}

h1, h2, h3 {
    color: #F4F7FC;
}

p, label {
    color: #C5CDDA;
}

.metric-card {
    background: #131E30;
    border: 1px solid #25354B;
    border-radius: 14px;
    padding: 20px;
    min-height: 115px;
}

.metric-label {
    color: #9AA9BC;
    font-size: 14px;
}

.metric-value {
    color: #FFFFFF;
    font-size: 27px;
    font-weight: 700;
    margin-top: 8px;
}

.hero {
    background: linear-gradient(120deg, #142B40, #102039);
    border: 1px solid #29465C;
    border-radius: 18px;
    padding: 26px;
    margin-bottom: 25px;
}

.hero h1 {
    color: #FFFFFF;
    margin-bottom: 8px;
}

.hero p {
    color: #AFC4D7;
    margin-bottom: 0;
}

.small-note {
    color: #91A2B8;
    font-size: 12px;
}

div.stButton > button {
    background-color: #13B8A6;
    color: #06131C;
    border: none;
    border-radius: 9px;
    font-weight: 700;
}

div.stButton > button:hover {
    background-color: #38D6C1;
    color: #06131C;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------

st.sidebar.markdown("# 📦 SmartStock AI")
st.sidebar.caption("Inventory Intelligence Platform")

page = st.sidebar.radio(
    "NAVIGATION",
    [
        "Overview",
        "Inventory",
        "Reorder Assistant",
        "Data & Settings"
    ]
)

st.sidebar.divider()

st.sidebar.caption("PROJECT")
st.sidebar.write("Smart inventory risk analysis")
st.sidebar.write("Python • SQL • Streamlit")

st.sidebar.caption(
    "Demo records are fictional and for demonstration only."
)


# --------------------------------------------------
# PREPARE ANALYSED DATA
# --------------------------------------------------

raw_data = st.session_state.inventory_data
df = analyse_inventory(raw_data)


# --------------------------------------------------
# HELPER: KPI CARD
# --------------------------------------------------

def metric_card(label, value):

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# --------------------------------------------------
# OVERVIEW PAGE
# --------------------------------------------------

if page == "Overview":

    st.markdown("""
    <div class="hero">
        <h1>SmartStock AI</h1>
        <p>
        Understand inventory risks, identify products
        that need replenishment, and make smarter stock decisions.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Business Overview")

    total_products = len(df)

    critical_count = len(
        df[df["status"].isin(["Critical", "Out of Stock"])]
    )

    reorder_count = len(
        df[df["status"] == "Reorder Soon"]
    )

    healthy_count = len(
        df[df["status"] == "Healthy"]
    )

    inventory_value = df["inventory_value"].sum()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        metric_card("Total Products", total_products)

    with col2:
        metric_card("Critical / Out of Stock", critical_count)

    with col3:
        metric_card("Reorder Soon", reorder_count)

    with col4:
        metric_card(
            "Inventory Value",
            f"₹{inventory_value:,.0f}"
        )

    st.write("")

    left, right = st.columns(2)

    with left:

        st.subheader("Inventory Status")

        status_counts = (
            df["status"]
            .value_counts()
            .reindex(
                ["Healthy", "Reorder Soon", "Critical", "Out of Stock"],
                fill_value=0
            )
        )

        st.bar_chart(status_counts)

    with right:

        st.subheader("Stock by Category")

        category_stock = (
            df.groupby("category")["stock"]
            .sum()
            .sort_values(ascending=False)
        )

        st.bar_chart(category_stock)

    st.subheader("Products Requiring Attention")

    attention = df[
        df["status"].isin(
            ["Critical", "Out of Stock", "Reorder Soon"]
        )
    ]

    if len(attention) > 0:

        st.dataframe(
            attention[
                [
                    "product_name",
                    "category",
                    "stock",
                    "days_remaining",
                    "status"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

    else:
        st.success("All products have sufficient stock.")

    st.caption(f"Data source: {st.session_state.data_source}")


# --------------------------------------------------
# INVENTORY PAGE
# --------------------------------------------------

elif page == "Inventory":

    st.title("Inventory Management")
    st.caption("Search, filter and review your product inventory.")

    search = st.text_input(
        "Search product",
        placeholder="Enter a product name..."
    )

    categories = ["All"] + sorted(
        df["category"].dropna().unique().tolist()
    )

    selected_category = st.selectbox(
        "Filter by category",
        categories
    )

    filtered = df.copy()

    if search:
        filtered = filtered[
            filtered["product_name"].str.contains(
                search,
                case=False,
                na=False
            )
        ]

    if selected_category != "All":
        filtered = filtered[
            filtered["category"] == selected_category
        ]

    display_columns = [
        "product_id",
        "product_name",
        "category",
        "stock",
        "daily_demand",
        "days_remaining",
        "reorder_point",
        "status"
    ]

    st.write(f"Products found: **{len(filtered)}**")

    st.dataframe(
        filtered[display_columns],
        use_container_width=True,
        hide_index=True
    )

    csv_data = filtered.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download Inventory CSV",
        data=csv_data,
        file_name="smartstock_inventory_report.csv",
        mime="text/csv"
    )


# --------------------------------------------------
# REORDER ASSISTANT PAGE
# --------------------------------------------------

elif page == "Reorder Assistant":

    st.title("Reorder Assistant")

    st.write(
        "Identify products that may run out before new stock arrives."
    )

    reorder_df = df[
        df["status"].isin(
            ["Critical", "Out of Stock", "Reorder Soon"]
        )
    ].copy()

    if reorder_df.empty:

        st.success("No products currently require replenishment.")

    else:

        for _, row in reorder_df.iterrows():

            with st.container(border=True):

                st.subheader(row["product_name"])

                col1, col2, col3 = st.columns(3)

                col1.metric("Current Stock", int(row["stock"]))

                col2.metric(
                    "Days Remaining",
                    int(row["days_remaining"])
                    if row["days_remaining"] < 999 else "N/A"
                )

                col3.metric(
                    "Suggested Reorder",
                    int(row["reorder_qty"])
                )

                st.write(f"**Status:** {row['status']}")

                st.write(
                    f"**Reorder Point:** "
                    f"{int(row['reorder_point'])} units"
                )

                if row["stock"] <= 0:

                    explanation = (
                        "This product is out of stock. "
                        "Review replenishment immediately."
                    )

                elif row["days_remaining"] <= row["lead_time"]:

                    explanation = (
                        "Current stock may not last until the next "
                        "delivery. Prioritise this product."
                    )

                else:

                    explanation = (
                        "Stock has reached its calculated reorder "
                        "level. Plan replenishment."
                    )

                st.info(explanation)

    st.caption(
        "Recommendations are rule-based estimates, not automatic purchase orders."
    )


# --------------------------------------------------
# DATA AND SETTINGS PAGE
# --------------------------------------------------

elif page == "Data & Settings":

    st.title("Data & Settings")

    st.subheader("Current Data Source")

    st.info(st.session_state.data_source)

    st.divider()

    st.subheader("Upload Inventory CSV")

    st.write(
        "Upload a CSV containing the required inventory columns."
    )

    uploaded_file = st.file_uploader(
        "Choose CSV file",
        type=["csv"]
    )

    if uploaded_file is not None:

        try:

            uploaded_data = pd.read_csv(uploaded_file)

            missing_columns = [
                column for column in COLUMNS
                if column not in uploaded_data.columns
            ]

            if missing_columns:

                st.error(
                    "Missing required columns: "
                    + ", ".join(missing_columns)
                )

            else:

                if st.button("Use Uploaded Inventory"):

                    st.session_state.inventory_data = (
                        uploaded_data[COLUMNS].copy()
                    )

                    st.session_state.data_source = "Uploaded CSV"

                    st.success("Inventory data loaded successfully!")

                    st.rerun()

        except Exception as error:

            st.error(f"Could not read the CSV: {error}")

    st.divider()

    st.subheader("Demo Data")

    if st.button("Restore Demo Inventory"):

        st.session_state.inventory_data = get_demo_data()

        st.session_state.data_source = "Demo data"

        st.success("Demo inventory restored.")

        st.rerun()

    sample_csv = get_demo_data().to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download Sample CSV",
        data=sample_csv,
        file_name="smartstock_sample_inventory.csv",
        mime="text/csv"
    )

    st.divider()

    st.subheader("MySQL Connection")

    st.write(
        "Optional: Connect your MySQL database to load inventory records."
    )

    if not MYSQL_AVAILABLE:

        st.warning(
            "MySQL connector is not installed. "
            "Install mysql-connector-python to enable this feature."
        )

    else:

        if st.button("Load Inventory from MySQL"):

            try:

                connection = mysql.connector.connect(
                    host=os.getenv("SMARTSTOCK_DB_HOST", "127.0.0.1"),
                    user=os.getenv("SMARTSTOCK_DB_USER", "root"),
                    password=os.getenv("SMARTSTOCK_DB_PASSWORD", ""),
                    database=os.getenv("SMARTSTOCK_DB_NAME", "smartstock"),
                    port=int(os.getenv("SMARTSTOCK_DB_PORT", "3306"))
                )

                mysql_data = pd.read_sql(
                    "SELECT * FROM inventory",
                    connection
                )

                connection.close()

                missing_columns = [
                    column for column in COLUMNS
                    if column not in mysql_data.columns
                ]

                if missing_columns:

                    st.error(
                        "MySQL table is missing: "
                        + ", ".join(missing_columns)
                    )

                else:

                    st.session_state.inventory_data = (
                        mysql_data[COLUMNS].copy()
                    )

                    st.session_state.data_source = "MySQL database"

                    st.success("MySQL inventory loaded successfully!")

                    st.rerun()

            except Exception as error:

                st.error(
                    "Could not connect to MySQL. "
                    "Check your database, table and environment settings. "
                    f"Details: {error}"
                )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.sidebar.divider()
st.sidebar.caption("SmartStock AI | Portfolio Project")