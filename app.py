
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(page_title="SalesPy", page_icon="📊", layout="wide")

# ── Data ─────────────────────────────────────────────────────
@st.cache_data
def load_data():
    np.random.seed(42)
    n = 500
    categories = ["Electronics", "Clothing", "Groceries", "Furniture", "Sports"]
    regions    = ["North", "South", "East", "West"]
    dates      = pd.date_range("2023-01-01", "2023-12-31", periods=n)

    df = pd.DataFrame({
        "Date":     np.random.choice(dates, n),
        "Category": np.random.choice(categories, n),
        "Region":   np.random.choice(regions, n),
        "Units":    np.random.randint(1, 50, n),
        "Price":    np.round(np.random.uniform(10, 500, n), 2),
        "Discount": np.random.choice([0, 5, 10, 15, 20], n),
    })
    df.loc[np.random.choice(n, 20, replace=False), "Price"] = np.nan
    df = pd.concat([df, df.sample(15)], ignore_index=True)
    df = df.drop_duplicates()
    df["Price"]    = df["Price"].fillna(df["Price"].median())
    df["Revenue"]  = df["Units"] * df["Price"] * (1 - df["Discount"] / 100)
    df["Date"]     = pd.to_datetime(df["Date"])
    df["Month"]    = df["Date"].dt.strftime("%b")
    df["MonthNum"] = df["Date"].dt.month
    return df.sort_values("Date").reset_index(drop=True)

df = load_data()
COLORS = ["#4361EE","#F72585","#7209B7","#4CC9F0","#06D6A0"]
BG     = "#0f172a"
CARD   = "#1e293b"

# ── Sidebar ──────────────────────────────────────────────────
st.sidebar.title("📊 SalesPy Filters")
sel_cat = st.sidebar.multiselect("Category", df["Category"].unique().tolist(),
                                  default=df["Category"].unique().tolist())
sel_reg = st.sidebar.multiselect("Region", df["Region"].unique().tolist(),
                                  default=df["Region"].unique().tolist())
disc    = st.sidebar.slider("Discount (%)", 0, 20, (0, 20), step=5)

fdf = df[
    df["Category"].isin(sel_cat) &
    df["Region"].isin(sel_reg) &
    df["Discount"].between(disc[0], disc[1])
]

st.sidebar.markdown(f"**Rows:** {len(fdf)}")
st.sidebar.download_button("⬇️ Download CSV",
    fdf.to_csv(index=False).encode(), "filtered_sales.csv", "text/csv")

# ── Header ───────────────────────────────────────────────────
st.title("📊 SalesPy — Retail Sales Dashboard")
st.caption("Retail Sales Analysis · Python + Streamlit + Plotly")
st.markdown("---")

# ── KPIs ─────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
k1.metric("💰 Total Revenue",    f"₹{fdf['Revenue'].sum():,.0f}")
k2.metric("📦 Units Sold",        f"{fdf['Units'].sum():,}")
k3.metric("🧾 Avg Order Value",   f"₹{fdf['Revenue'].mean():,.2f}")
k4.metric("🏆 Top Category",
          fdf.groupby("Category")["Revenue"].sum().idxmax() if not fdf.empty else "N/A")

st.markdown("---")

# ── Charts ───────────────────────────────────────────────────
def dark(fig):
    fig.update_layout(
        paper_bgcolor=BG, plot_bgcolor=CARD,
        font_color="white", margin=dict(l=10, r=10, t=40, b=10)
    )
    return fig

c1, c2 = st.columns(2)

# 1 Monthly trend
with c1:
    st.subheader("📈 Monthly Revenue Trend")
    monthly = fdf.groupby(["MonthNum","Month"])["Revenue"].sum().reset_index().sort_values("MonthNum")
    fig = px.line(monthly, x="Month", y="Revenue", markers=True,
                  color_discrete_sequence=["#4CC9F0"])
    fig.update_traces(fill="tozeroy", fillcolor="rgba(76,201,240,0.1)")
    st.plotly_chart(dark(fig), use_container_width=True)

# 2 Category bar
with c2:
    st.subheader("🏷️ Revenue by Category")
    cat_rev = fdf.groupby("Category")["Revenue"].sum().reset_index().sort_values("Revenue")
    fig = px.bar(cat_rev, x="Revenue", y="Category", orientation="h",
                 color="Category", color_discrete_sequence=COLORS)
    fig.update_layout(showlegend=False)
    st.plotly_chart(dark(fig), use_container_width=True)

c3, c4 = st.columns(2)

# 3 Region pie
with c3:
    st.subheader("🌍 Revenue by Region")
    reg_rev = fdf.groupby("Region")["Revenue"].sum().reset_index()
    fig = px.pie(reg_rev, names="Region", values="Revenue",
                 color_discrete_sequence=COLORS, hole=0.35)
    fig.update_traces(textfont_color="white")
    st.plotly_chart(dark(fig), use_container_width=True)

# 4 Units bar
with c4:
    st.subheader("📦 Units Sold by Category")
    cat_units = fdf.groupby("Category")["Units"].sum().reset_index()
    fig = px.bar(cat_units, x="Category", y="Units",
                 color="Category", color_discrete_sequence=COLORS)
    fig.update_layout(showlegend=False)
    st.plotly_chart(dark(fig), use_container_width=True)

# 5 Box plot full width
st.subheader("📉 Revenue Distribution by Category")
fig = px.box(fdf, x="Category", y="Revenue",
             color="Category", color_discrete_sequence=COLORS)
fig.update_layout(showlegend=False)
st.plotly_chart(dark(fig), use_container_width=True)

# ── Table ────────────────────────────────────────────────────
st.markdown("---")
st.subheader("🗃️ Data Preview")
st.dataframe(
    fdf[["Date","Category","Region","Units","Price","Discount","Revenue"]].head(50),
    use_container_width=True
)
st.caption("SalesPy v1.0 · Built by Aryan Nagar")
