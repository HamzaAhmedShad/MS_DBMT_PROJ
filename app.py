"""
app.py — Customer Segmentation Management System
Streamlit dashboard with full CRUD + analytics
Run: streamlit run app.py
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import date, datetime
import db

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SegmentIQ",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Design tokens & global CSS ────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500&family=Inter:wght@300;400;500&display=swap');

/* ── Root variables ── */
:root {
    --bg:        #060912;
    --surface:   #0D1526;
    --surface2:  #111d35;
    --border:    #1e2d4a;
    --accent:    #00E5C3;
    --accent2:   #F7B731;
    --accent3:   #FF6B6B;
    --accent4:   #7C5CFC;
    --text:      #E8EEF8;
    --muted:     #6B7FA3;
    --font-head: 'Syne', sans-serif;
    --font-mono: 'JetBrains Mono', monospace;
    --font-body: 'Inter', sans-serif;
}

/* ── Global reset ── */
html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--font-body) !important;
}

[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}

/* ── Sidebar nav buttons ── */
[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    background: transparent;
    border: 1px solid transparent;
    color: var(--muted);
    font-family: var(--font-body);
    font-size: 0.85rem;
    font-weight: 500;
    text-align: left;
    padding: 0.6rem 1rem;
    border-radius: 8px;
    transition: all 0.2s;
    letter-spacing: 0.02em;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: var(--border);
    color: var(--text);
    border-color: var(--border);
}

/* ── Hide default Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* ── Main content padding ── */
.main .block-container {
    padding: 1.5rem 2rem 3rem 2rem !important;
    max-width: 1400px !important;
}

/* ── KPI cards ── */
.kpi-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.3s;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--accent-color, var(--accent));
}
.kpi-card:hover { border-color: var(--accent-color, var(--accent)); }
.kpi-label {
    font-family: var(--font-mono);
    font-size: 0.65rem;
    font-weight: 500;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 0.5rem;
}
.kpi-value {
    font-family: var(--font-head);
    font-size: 2rem;
    font-weight: 800;
    color: var(--text);
    line-height: 1;
    margin-bottom: 0.3rem;
}
.kpi-sub {
    font-size: 0.72rem;
    color: var(--muted);
}
.kpi-icon {
    position: absolute;
    top: 1rem; right: 1.2rem;
    font-size: 1.5rem;
    opacity: 0.15;
}

/* ── Section headings ── */
.section-title {
    font-family: var(--font-head);
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--text);
    margin-bottom: 0.2rem;
    letter-spacing: -0.02em;
}
.section-sub {
    font-family: var(--font-body);
    font-size: 0.82rem;
    color: var(--muted);
    margin-bottom: 1.2rem;
}

/* ── Page hero ── */
.page-hero {
    background: linear-gradient(135deg, var(--surface) 0%, #0a1628 100%);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.page-hero::after {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(0,229,195,0.08) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-title {
    font-family: var(--font-head);
    font-size: 2.2rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    background: linear-gradient(90deg, #E8EEF8 0%, var(--accent) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.4rem;
}
.hero-sub {
    font-size: 0.9rem;
    color: var(--muted);
    font-weight: 300;
}

/* ── Chart containers ── */
.chart-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
}
.chart-title {
    font-family: var(--font-mono);
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--muted);
    margin-bottom: 0.8rem;
}

/* ── Tables ── */
[data-testid="stDataFrame"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    overflow: hidden;
}

/* ── Forms & inputs ── */
[data-testid="stForm"] {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.5rem;
}
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div,
.stDateInput > div > div > input {
    background: var(--bg) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: var(--font-body) !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(0,229,195,0.12) !important;
}

/* ── Primary buttons ── */
.stButton > button[kind="primary"],
.stFormSubmitButton > button {
    background: var(--accent) !important;
    color: #060912 !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: var(--font-body) !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.03em !important;
    padding: 0.55rem 1.4rem !important;
    transition: all 0.2s !important;
}
.stButton > button[kind="primary"]:hover,
.stFormSubmitButton > button:hover {
    background: #00c4a8 !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 16px rgba(0,229,195,0.25) !important;
}

/* ── Secondary / danger buttons ── */
.stButton > button[kind="secondary"] {
    background: transparent !important;
    border: 1px solid var(--border) !important;
    color: var(--muted) !important;
    border-radius: 8px !important;
    font-size: 0.82rem !important;
}

/* ── Alert / success / error ── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    font-family: var(--font-body) !important;
    font-size: 0.84rem !important;
}

/* ── Tabs ── */
[data-testid="stTabs"] [role="tablist"] {
    border-bottom: 1px solid var(--border) !important;
    gap: 0 !important;
}
[data-testid="stTabs"] [role="tab"] {
    font-family: var(--font-body) !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    color: var(--muted) !important;
    padding: 0.6rem 1.2rem !important;
    border-radius: 8px 8px 0 0 !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
    background: transparent !important;
}

/* ── Tag badges ── */
.badge {
    display: inline-block;
    padding: 0.2rem 0.65rem;
    border-radius: 20px;
    font-family: var(--font-mono);
    font-size: 0.65rem;
    font-weight: 500;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.badge-basic    { background: rgba(124,92,252,0.15); color: #a78bfa; border: 1px solid rgba(124,92,252,0.3); }
.badge-inter    { background: rgba(247,183,49,0.12); color: #fbbf24; border: 1px solid rgba(247,183,49,0.3); }
.badge-advanced { background: rgba(0,229,195,0.12);  color: var(--accent); border: 1px solid rgba(0,229,195,0.3); }

/* ── SQL code blocks ── */
.sql-block {
    background: #080e1c;
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    border-radius: 0 10px 10px 0;
    padding: 1rem 1.2rem;
    font-family: var(--font-mono);
    font-size: 0.75rem;
    color: #a8c7fa;
    line-height: 1.7;
    white-space: pre-wrap;
    overflow-x: auto;
    margin: 0.5rem 0 1rem 0;
}

/* ── Divider ── */
.divider {
    height: 1px;
    background: var(--border);
    margin: 1.5rem 0;
}

/* ── Sidebar logo ── */
.sidebar-logo {
    font-family: var(--font-head);
    font-size: 1.4rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    padding: 1rem 0 0.3rem 0;
}
.logo-accent { color: var(--accent); }
.sidebar-tagline {
    font-family: var(--font-mono);
    font-size: 0.6rem;
    color: var(--muted);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 1.5rem;
}
.nav-section {
    font-family: var(--font-mono);
    font-size: 0.58rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.15em;
    padding: 0.8rem 0 0.4rem 0;
    opacity: 0.6;
}
</style>
""", unsafe_allow_html=True)

# ── Plotly theme ──────────────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#6B7FA3", size=11),
    margin=dict(l=10, r=10, t=30, b=10),
    colorway=["#00E5C3", "#F7B731", "#7C5CFC", "#FF6B6B", "#4ECDC4", "#45B7D1"],
    xaxis=dict(gridcolor="#1e2d4a", linecolor="#1e2d4a", tickcolor="#1e2d4a"),
    yaxis=dict(gridcolor="#1e2d4a", linecolor="#1e2d4a", tickcolor="#1e2d4a"),
)
SEGMENT_COLORS = {
    "High-Value Buyers": "#00E5C3",
    "Loyal Customers":   "#7C5CFC",
    "At-Risk Customers": "#F7B731",
    "Lost Customers":    "#FF6B6B",
}


# ── Session state ─────────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"
if "conn" not in st.session_state:
    st.session_state.conn = None
if "connected" not in st.session_state:
    st.session_state.connected = False


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class='sidebar-logo'>Segment<span class='logo-accent'>IQ</span></div>
    <div class='sidebar-tagline'>Customer Intelligence Platform</div>
    """, unsafe_allow_html=True)

    # Connection panel
    with st.expander("⚙ Database Connection", expanded=not st.session_state.connected):
        host = st.text_input("Host", value="localhost", key="db_host")
        port = st.number_input("Port", value=3306, step=1, key="db_port")
        user = st.text_input("User", value="root", key="db_user")
        pwd  = st.text_input("Password", type="password", key="db_pwd")
        dbname = st.text_input("Database", value="customer_segmentation", key="db_name")

        if st.button("Connect", type="primary"):
            conn = db.get_connection(host, user, pwd, dbname, int(port))
            if conn and conn.is_connected():
                st.session_state.conn = conn
                st.session_state.connected = True
                st.success("Connected ✓")
                st.rerun()
            else:
                st.error("Connection failed. Check credentials.")

    if st.session_state.connected:
        st.markdown("<div style='height:4px;background:linear-gradient(90deg,#00E5C3,#7C5CFC);border-radius:2px;margin:0.5rem 0 1rem;'></div>", unsafe_allow_html=True)

        st.markdown("<div class='nav-section'>Overview</div>", unsafe_allow_html=True)
        for page in ["Dashboard"]:
            if st.button(f"◈  {page}", key=f"nav_{page}"):
                st.session_state.page = page

        st.markdown("<div class='nav-section'>Data Management</div>", unsafe_allow_html=True)
        for page in ["Customers", "Products", "Transactions", "Behavioral Metrics", "Segmentation"]:
            if st.button(f"◆  {page}", key=f"nav_{page}"):
                st.session_state.page = page

        st.markdown("<div class='nav-section'>Analytics</div>", unsafe_allow_html=True)
        for page in ["Query Pack"]:
            if st.button(f"◇  {page}", key=f"nav_{page}"):
                st.session_state.page = page

        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

        # Live mini-stats
        try:
            c = st.session_state.conn
            n_cust  = db.kpi_total_customers(c)
            n_prod  = db.kpi_total_products(c)
            n_trans = db.kpi_total_transactions(c)
            st.markdown(f"""
            <div style='font-family:var(--font-mono);font-size:0.62rem;color:var(--muted);line-height:2;'>
            CUSTOMERS &nbsp;&nbsp;<span style='color:#E8EEF8'>{n_cust}</span><br>
            PRODUCTS &nbsp;&nbsp;&nbsp;<span style='color:#E8EEF8'>{n_prod}</span><br>
            TRANSACTIONS <span style='color:#E8EEF8'>{n_trans}</span>
            </div>
            """, unsafe_allow_html=True)
        except Exception:
            pass


# ── Guard: require connection ─────────────────────────────────────────────────
if not st.session_state.connected:
    st.markdown("""
    <div style='display:flex;flex-direction:column;align-items:center;justify-content:center;
                height:70vh;gap:1rem;'>
        <div style='font-family:Syne,sans-serif;font-size:3rem;font-weight:800;
                    letter-spacing:-0.04em;background:linear-gradient(90deg,#E8EEF8,#00E5C3);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;'>
            SegmentIQ
        </div>
        <div style='font-family:JetBrains Mono,monospace;font-size:0.75rem;
                    color:#6B7FA3;letter-spacing:0.15em;text-transform:uppercase;'>
            Customer Intelligence Platform
        </div>
        <div style='margin-top:1rem;font-size:0.9rem;color:#6B7FA3;text-align:center;max-width:400px;'>
            Connect to your MySQL database using the panel in the sidebar to get started.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

conn = st.session_state.conn
page = st.session_state.page


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if page == "Dashboard":
    st.markdown("""
    <div class='page-hero'>
        <div class='hero-title'>Dashboard</div>
        <div class='hero-sub'>Live snapshot of your customer segmentation database</div>
    </div>
    """, unsafe_allow_html=True)

    # KPIs
    total_cust  = db.kpi_total_customers(conn)
    total_prod  = db.kpi_total_products(conn)
    total_rev   = db.kpi_total_revenue(conn)
    total_trans = db.kpi_total_transactions(conn)
    avg_order   = db.kpi_avg_order_value(conn)
    n_segs      = db.kpi_segments(conn)

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    cards = [
        (k1, "Customers",     f"{total_cust:,}",       "registered profiles",    "#00E5C3", "👥"),
        (k2, "Products",      f"{total_prod:,}",        "in catalogue",           "#7C5CFC", "📦"),
        (k3, "Total Revenue", f"${total_rev:,.2f}",     "lifetime value",         "#F7B731", "💰"),
        (k4, "Transactions",  f"{total_trans:,}",       "purchase records",       "#FF6B6B", "🧾"),
        (k5, "Avg Order",     f"${avg_order:,.2f}",     "per transaction",        "#4ECDC4", "📊"),
        (k6, "Segments",      f"{n_segs}",              "customer segments",      "#45B7D1", "🎯"),
    ]
    for col, label, value, sub, color, icon in cards:
        with col:
            st.markdown(f"""
            <div class='kpi-card' style='--accent-color:{color}'>
                <div class='kpi-icon'>{icon}</div>
                <div class='kpi-label'>{label}</div>
                <div class='kpi-value'>{value}</div>
                <div class='kpi-sub'>{sub}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

    # Row 1: Revenue trend + Category breakdown
    c1, c2 = st.columns([2, 1])
    with c1:
        monthly = db.chart_monthly_revenue(conn)
        if not monthly.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=monthly["Month"], y=monthly["Revenue"],
                mode="lines+markers",
                line=dict(color="#00E5C3", width=2.5),
                marker=dict(size=6, color="#00E5C3"),
                fill="tozeroy",
                fillcolor="rgba(0,229,195,0.06)",
                name="Revenue"
            ))
            fig.update_layout(**PLOTLY_LAYOUT, title="Monthly Revenue Trend",
                              title_font=dict(color="#E8EEF8", size=13, family="Syne"),
                              height=260)
            st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        cat_rev = db.chart_category_revenue(conn)
        if not cat_rev.empty:
            fig = px.pie(cat_rev, values="Revenue", names="Category",
                         hole=0.55,
                         color_discrete_sequence=["#00E5C3","#7C5CFC","#F7B731","#FF6B6B","#4ECDC4"])
            fig.update_layout(**PLOTLY_LAYOUT, title="Revenue by Category",
                              title_font=dict(color="#E8EEF8", size=13, family="Syne"),
                              height=260,
                              legend=dict(font=dict(size=10)))
            fig.update_traces(textposition="inside", textinfo="percent",
                              textfont_size=10)
            st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)

    # Row 2: Top customers + Segment donut + RFM scatter
    c3, c4, c5 = st.columns([1.5, 1, 1.5])
    with c3:
        top_cust = db.chart_top_customers(conn)
        if not top_cust.empty:
            fig = go.Figure(go.Bar(
                x=top_cust["TotalSpent"],
                y=top_cust["Customer"],
                orientation="h",
                marker=dict(
                    color=top_cust["TotalSpent"],
                    colorscale=[[0,"#1e2d4a"],[1,"#00E5C3"]],
                    showscale=False
                )
            ))
            top_customers_layout = dict(
                **PLOTLY_LAYOUT,
                title="Top Customers by Spend",
                title_font=dict(color="#E8EEF8", size=13, family="Syne"),
                height=280,
            )
            top_customers_layout["yaxis"] = dict(**PLOTLY_LAYOUT["yaxis"], autorange="reversed")
            fig.update_layout(**top_customers_layout)
            st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)

    with c4:
        seg = db.chart_segment_distribution(conn)
        if not seg.empty:
            colors = [SEGMENT_COLORS.get(s, "#6B7FA3") for s in seg["SegmentLabel"]]
            fig = go.Figure(go.Pie(
                labels=seg["SegmentLabel"],
                values=seg["Customers"],
                hole=0.6,
                marker=dict(colors=colors, line=dict(color="#060912", width=2))
            ))
            fig.update_layout(**PLOTLY_LAYOUT, title="Segment Distribution",
                              title_font=dict(color="#E8EEF8", size=13, family="Syne"),
                              height=280,
                              legend=dict(font=dict(size=9), orientation="v"))
            fig.update_traces(textinfo="value", textfont_size=11)
            st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)

    with c5:
        rfm = db.chart_rfm(conn)
        if not rfm.empty:
            seg_colors = [SEGMENT_COLORS.get(s, "#6B7FA3") for s in rfm["SegmentLabel"]]
            fig = go.Figure(go.Scatter(
                x=rfm["Frequency"], y=rfm["Monetary"],
                mode="markers+text",
                marker=dict(size=rfm["Recency"].clip(lower=5)/2 + 10,
                            color=seg_colors, opacity=0.85,
                            line=dict(width=1, color="#060912")),
                text=rfm["Customer"].apply(lambda x: x.split()[0]),
                textposition="top center",
                textfont=dict(size=8, color="#6B7FA3"),
            ))
            fig.update_layout(**PLOTLY_LAYOUT, title="RFM Bubble Chart",
                              title_font=dict(color="#E8EEF8", size=13, family="Syne"),
                              height=280,
                              xaxis_title="Frequency", yaxis_title="Monetary ($)")
            st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: CUSTOMERS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Customers":
    st.markdown("""
    <div class='page-hero'>
        <div class='hero-title'>Customers</div>
        <div class='hero-sub'>View, add, edit, and delete customer records</div>
    </div>
    """, unsafe_allow_html=True)

    tab_view, tab_add, tab_edit, tab_del = st.tabs(
        ["📋  View All", "➕  Add Customer", "✏️  Edit Customer", "🗑  Delete Customer"]
    )

    with tab_view:
        df = db.get_all_customers(conn)
        if not df.empty:
            st.markdown(f"<div class='section-sub'>{len(df)} customers in database</div>", unsafe_allow_html=True)
            st.dataframe(df, use_container_width=True, hide_index=True,
                         column_config={
                             "CustomerID":       st.column_config.NumberColumn("ID", width="small"),
                             "RegistrationDate": st.column_config.DateColumn("Registered"),
                             "Age":              st.column_config.NumberColumn("Age", width="small"),
                         })
        else:
            st.info("No customers found.")

    with tab_add:
        st.markdown("<div class='section-title'>Add New Customer</div>", unsafe_allow_html=True)
        with st.form("add_customer_form", clear_on_submit=True):
            a1, a2 = st.columns(2)
            first = a1.text_input("First Name *")
            last  = a2.text_input("Last Name *")
            b1, b2, b3 = st.columns(3)
            age    = b1.number_input("Age", min_value=0, max_value=120, step=1, value=25)
            gender = b2.selectbox("Gender", ["", "Male", "Female", "Non-binary", "Prefer not to say"])
            reg    = b3.date_input("Registration Date", value=date.today())
            c1, c2 = st.columns(2)
            email = c1.text_input("Email *")
            phone = c2.text_input("Phone")

            submitted = st.form_submit_button("Add Customer", type="primary")
            if submitted:
                if not first or not last or not email:
                    st.error("First name, last name, and email are required.")
                else:
                    ok, new_id = db.add_customer(conn, first, last,
                                                  int(age) if age else None,
                                                  gender or None, email,
                                                  phone or None, reg)
                    if ok:
                        st.success(f"Customer added with ID {new_id} ✓")
                        st.rerun()

    with tab_edit:
        st.markdown("<div class='section-title'>Edit Existing Customer</div>", unsafe_allow_html=True)
        df_c = db.get_all_customers(conn)
        if df_c.empty:
            st.info("No customers to edit.")
        else:
            opts = {f"[{r.CustomerID}] {r.FirstName} {r.LastName}": r.CustomerID
                    for _, r in df_c.iterrows()}
            sel = st.selectbox("Select customer", list(opts.keys()))
            cid = opts[sel]
            row = df_c[df_c.CustomerID == cid].iloc[0]

            with st.form("edit_customer_form"):
                a1, a2 = st.columns(2)
                first = a1.text_input("First Name", value=row.FirstName)
                last  = a2.text_input("Last Name",  value=row.LastName)
                b1, b2, b3 = st.columns(3)
                age    = b1.number_input("Age", value=int(row.Age) if pd.notna(row.Age) else 0,
                                          min_value=0, max_value=120)
                gender = b2.selectbox("Gender",
                                       ["", "Male", "Female", "Non-binary", "Prefer not to say"],
                                       index=["", "Male", "Female", "Non-binary", "Prefer not to say"]
                                              .index(row.Gender) if pd.notna(row.Gender) and row.Gender in
                                              ["", "Male", "Female", "Non-binary", "Prefer not to say"] else 0)
                reg    = b3.date_input("Registration Date",
                                        value=pd.to_datetime(row.RegistrationDate).date()
                                        if pd.notna(row.RegistrationDate) else date.today())
                c1, c2 = st.columns(2)
                email = c1.text_input("Email", value=row.Email)
                phone = c2.text_input("Phone", value=row.Phone if pd.notna(row.Phone) else "")

                if st.form_submit_button("Save Changes", type="primary"):
                    ok, _ = db.update_customer(conn, cid, first, last,
                                                int(age) if age else None,
                                                gender or None, email,
                                                phone or None, reg)
                    if ok:
                        st.success("Customer updated ✓")
                        st.rerun()

    with tab_del:
        st.markdown("<div class='section-title'>Delete Customer</div>", unsafe_allow_html=True)
        st.warning("⚠️ Deleting a customer is permanent and may fail if they have linked transactions.")
        df_c = db.get_all_customers(conn)
        if df_c.empty:
            st.info("No customers to delete.")
        else:
            opts = {f"[{r.CustomerID}] {r.FirstName} {r.LastName}": r.CustomerID
                    for _, r in df_c.iterrows()}
            sel = st.selectbox("Select customer to delete", list(opts.keys()), key="del_cust")
            cid = opts[sel]
            if st.button("Confirm Delete", type="primary", key="del_cust_btn"):
                ok, _ = db.delete_customer(conn, cid)
                if ok:
                    st.success("Customer deleted ✓")
                    st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: PRODUCTS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Products":
    st.markdown("""
    <div class='page-hero'>
        <div class='hero-title'>Products</div>
        <div class='hero-sub'>Manage your product catalogue</div>
    </div>
    """, unsafe_allow_html=True)

    tab_view, tab_add, tab_edit, tab_del = st.tabs(
        ["📋  View All", "➕  Add Product", "✏️  Edit Product", "🗑  Delete Product"]
    )

    with tab_view:
        df = db.get_all_products(conn)
        if not df.empty:
            st.markdown(f"<div class='section-sub'>{len(df)} products in catalogue</div>", unsafe_allow_html=True)
            # Product revenue chart
            prod_rev = db.chart_products_revenue(conn)
            if not prod_rev.empty:
                fig = go.Figure(go.Bar(
                    x=prod_rev["ProductName"], y=prod_rev["Revenue"],
                    marker=dict(color="#7C5CFC", opacity=0.85)
                ))
                fig.update_layout(**PLOTLY_LAYOUT, title="Top 10 Products by Revenue",
                                  title_font=dict(color="#E8EEF8", size=13, family="Syne"),
                                  height=220, xaxis_tickangle=-30)
                st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
                st.markdown("</div>", unsafe_allow_html=True)

            st.dataframe(df, use_container_width=True, hide_index=True,
                         column_config={
                             "ProductID": st.column_config.NumberColumn("ID", width="small"),
                             "Price":     st.column_config.NumberColumn("Price", format="$%.2f"),
                         })

    with tab_add:
        st.markdown("<div class='section-title'>Add New Product</div>", unsafe_allow_html=True)
        categories = ["Home Decor", "Kitchen", "Accessories", "Bags", "Clothing", "Electronics", "Other"]
        with st.form("add_product_form", clear_on_submit=True):
            a1, a2, a3 = st.columns(3)
            name     = a1.text_input("Product Name *")
            category = a2.selectbox("Category", categories)
            price    = a3.number_input("Price ($) *", min_value=0.01, step=0.01, format="%.2f")
            if st.form_submit_button("Add Product", type="primary"):
                if not name:
                    st.error("Product name is required.")
                else:
                    ok, new_id = db.add_product(conn, name, category, price)
                    if ok:
                        st.success(f"Product added with ID {new_id} ✓")
                        st.rerun()

    with tab_edit:
        st.markdown("<div class='section-title'>Edit Product</div>", unsafe_allow_html=True)
        df_p = db.get_all_products(conn)
        if df_p.empty:
            st.info("No products to edit.")
        else:
            opts = {f"[{r.ProductID}] {r.ProductName}": r.ProductID for _, r in df_p.iterrows()}
            sel  = st.selectbox("Select product", list(opts.keys()))
            pid  = opts[sel]
            row  = df_p[df_p.ProductID == pid].iloc[0]
            categories = ["Home Decor", "Kitchen", "Accessories", "Bags", "Clothing", "Electronics", "Other"]

            with st.form("edit_product_form"):
                a1, a2, a3 = st.columns(3)
                name     = a1.text_input("Product Name", value=row.ProductName)
                cat_idx  = categories.index(row.Category) if row.Category in categories else 0
                category = a2.selectbox("Category", categories, index=cat_idx)
                price    = a3.number_input("Price ($)", value=float(row.Price),
                                            min_value=0.01, step=0.01, format="%.2f")
                if st.form_submit_button("Save Changes", type="primary"):
                    ok, _ = db.update_product(conn, pid, name, category, price)
                    if ok:
                        st.success("Product updated ✓")
                        st.rerun()

    with tab_del:
        st.markdown("<div class='section-title'>Delete Product</div>", unsafe_allow_html=True)
        st.warning("⚠️ Products linked to transactions cannot be deleted.")
        df_p = db.get_all_products(conn)
        if df_p.empty:
            st.info("No products to delete.")
        else:
            opts = {f"[{r.ProductID}] {r.ProductName}": r.ProductID for _, r in df_p.iterrows()}
            sel  = st.selectbox("Select product to delete", list(opts.keys()), key="del_prod")
            pid  = opts[sel]
            if st.button("Confirm Delete", type="primary", key="del_prod_btn"):
                ok, _ = db.delete_product(conn, pid)
                if ok:
                    st.success("Product deleted ✓")
                    st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: TRANSACTIONS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Transactions":
    st.markdown("""
    <div class='page-hero'>
        <div class='hero-title'>Transactions</div>
        <div class='hero-sub'>Purchase history and new transaction entry</div>
    </div>
    """, unsafe_allow_html=True)

    tab_view, tab_add, tab_del = st.tabs(
        ["📋  View All", "➕  Add Transaction", "🗑  Delete Transaction"]
    )

    with tab_view:
        df = db.get_all_transactions(conn)
        if not df.empty:
            # Quick filters
            f1, f2, _ = st.columns([1, 1, 2])
            cats = ["All"] + sorted(df["Category"].dropna().unique().tolist())
            cat_filter = f1.selectbox("Filter by category", cats, key="trans_cat")
            search     = f2.text_input("Search customer name", key="trans_search")

            filtered = df.copy()
            if cat_filter != "All":
                filtered = filtered[filtered["Category"] == cat_filter]
            if search:
                filtered = filtered[filtered["Customer"].str.contains(search, case=False, na=False)]

            st.markdown(f"<div class='section-sub'>Showing {len(filtered)} of {len(df)} transactions</div>",
                        unsafe_allow_html=True)
            st.dataframe(filtered, use_container_width=True, hide_index=True,
                         column_config={
                             "TransactionID":   st.column_config.NumberColumn("ID", width="small"),
                             "TransactionDate": st.column_config.DatetimeColumn("Date"),
                             "TotalAmount":     st.column_config.NumberColumn("Total", format="$%.2f"),
                             "Quantity":        st.column_config.NumberColumn("Qty", width="small"),
                         })

    with tab_add:
        st.markdown("<div class='section-title'>Add New Transaction</div>", unsafe_allow_html=True)
        df_c = db.get_all_customers(conn)
        df_p = db.get_all_products(conn)

        if df_c.empty or df_p.empty:
            st.warning("You need at least one customer and one product to add a transaction.")
        else:
            cust_opts = {f"[{r.CustomerID}] {r.FirstName} {r.LastName}": r.CustomerID
                         for _, r in df_c.iterrows()}
            prod_opts = {f"[{r.ProductID}] {r.ProductName} — ${r.Price:.2f}": (r.ProductID, float(r.Price))
                         for _, r in df_p.iterrows()}

            with st.form("add_transaction_form", clear_on_submit=True):
                a1, a2 = st.columns(2)
                cust_sel = a1.selectbox("Customer *", list(cust_opts.keys()))
                prod_sel = a2.selectbox("Product *", list(prod_opts.keys()))

                b1, b2, b3 = st.columns(3)
                trans_date = b1.date_input("Transaction Date", value=date.today())
                qty        = b2.number_input("Quantity *", min_value=1, step=1, value=1)
                price_val  = prod_opts[prod_sel][1]
                auto_total = round(price_val * qty, 2)
                total      = b3.number_input("Total Amount ($)", value=auto_total,
                                              min_value=0.0, step=0.01, format="%.2f")

                st.markdown(f"""
                <div style='font-family:var(--font-mono);font-size:0.72rem;color:var(--muted);
                            padding:0.5rem;background:#080e1c;border-radius:6px;margin:0.5rem 0;'>
                Auto-calculated: {qty} × ${price_val:.2f} = <span style='color:#00E5C3'>${auto_total:.2f}</span>
                </div>
                """, unsafe_allow_html=True)

                if st.form_submit_button("Add Transaction", type="primary"):
                    cid = cust_opts[cust_sel]
                    pid, _ = prod_opts[prod_sel]
                    dt_str = datetime.combine(trans_date, datetime.min.time()).strftime("%Y-%m-%d %H:%M:%S")
                    ok, new_id = db.add_transaction(conn, cid, pid, dt_str, int(qty), float(total))
                    if ok:
                        st.success(f"Transaction {new_id} added ✓")
                        st.rerun()

    with tab_del:
        st.markdown("<div class='section-title'>Delete Transaction</div>", unsafe_allow_html=True)
        df_t = db.get_all_transactions(conn)
        if df_t.empty:
            st.info("No transactions.")
        else:
            opts = {f"[{r.TransactionID}] {r.Customer} — {r.ProductName} — ${r.TotalAmount:.2f}": r.TransactionID
                    for _, r in df_t.iterrows()}
            sel  = st.selectbox("Select transaction", list(opts.keys()), key="del_trans")
            tid  = opts[sel]
            if st.button("Confirm Delete", type="primary", key="del_trans_btn"):
                ok, _ = db.delete_transaction(conn, tid)
                if ok:
                    st.success("Transaction deleted ✓")
                    st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: BEHAVIORAL METRICS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Behavioral Metrics":
    st.markdown("""
    <div class='page-hero'>
        <div class='hero-title'>Behavioral Metrics</div>
        <div class='hero-sub'>Customer purchase behavior summaries — frequency, spending, and recency</div>
    </div>
    """, unsafe_allow_html=True)

    tab_view, tab_edit = st.tabs(["📋  View All", "✏️  Add / Update Metrics"])

    with tab_view:
        df = db.get_all_metrics(conn)
        if not df.empty:
            # Bar charts
            c1, c2, c3 = st.columns(3)
            with c1:
                fig = px.bar(df.sort_values("PurchaseFrequency", ascending=False),
                             x="Customer", y="PurchaseFrequency",
                             color_discrete_sequence=["#7C5CFC"])
                fig.update_layout(**PLOTLY_LAYOUT, title="Purchase Frequency",
                                  title_font=dict(color="#E8EEF8", size=12, family="Syne"),
                                  height=220, xaxis_tickangle=-30)
                st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
                st.markdown("</div>", unsafe_allow_html=True)

            with c2:
                fig = px.bar(df.sort_values("AverageSpending", ascending=False),
                             x="Customer", y="AverageSpending",
                             color_discrete_sequence=["#00E5C3"])
                fig.update_layout(**PLOTLY_LAYOUT, title="Average Spending ($)",
                                  title_font=dict(color="#E8EEF8", size=12, family="Syne"),
                                  height=220, xaxis_tickangle=-30)
                st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
                st.markdown("</div>", unsafe_allow_html=True)

            with c3:
                fig = px.bar(df.sort_values("RecencyOfPurchase", ascending=True),
                             x="Customer", y="RecencyOfPurchase",
                             color_discrete_sequence=["#F7B731"])
                fig.update_layout(**PLOTLY_LAYOUT, title="Recency (Days Since Last Purchase)",
                                  title_font=dict(color="#E8EEF8", size=12, family="Syne"),
                                  height=220, xaxis_tickangle=-30)
                st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
                st.markdown("</div>", unsafe_allow_html=True)

            st.dataframe(df, use_container_width=True, hide_index=True,
                         column_config={
                             "AverageSpending":  st.column_config.NumberColumn("Avg Spending", format="$%.2f"),
                             "RecencyOfPurchase": st.column_config.NumberColumn("Recency (days)"),
                         })

    with tab_edit:
        st.markdown("<div class='section-title'>Add / Update Customer Metrics</div>", unsafe_allow_html=True)
        df_c = db.get_all_customers(conn)
        if df_c.empty:
            st.info("No customers found.")
        else:
            opts = {f"[{r.CustomerID}] {r.FirstName} {r.LastName}": r.CustomerID
                    for _, r in df_c.iterrows()}
            with st.form("upsert_metrics_form", clear_on_submit=True):
                sel  = st.selectbox("Customer", list(opts.keys()))
                cid  = opts[sel]
                a1, a2, a3 = st.columns(3)
                freq    = a1.number_input("Purchase Frequency", min_value=0, step=1, value=1)
                avg_sp  = a2.number_input("Average Spending ($)", min_value=0.0, step=0.01, format="%.2f")
                recency = a3.number_input("Recency (days since last purchase)", min_value=0, step=1)
                if st.form_submit_button("Save Metrics", type="primary"):
                    ok, _ = db.upsert_metrics(conn, cid, int(freq), float(avg_sp), int(recency))
                    if ok:
                        st.success("Metrics saved ✓")
                        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: SEGMENTATION
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Segmentation":
    st.markdown("""
    <div class='page-hero'>
        <div class='hero-title'>Segmentation Results</div>
        <div class='hero-sub'>Customer cluster assignments and segment analytics</div>
    </div>
    """, unsafe_allow_html=True)

    tab_view, tab_add, tab_del = st.tabs(
        ["📋  View All", "➕  Add Result", "🗑  Delete Result"]
    )

    with tab_view:
        df = db.get_all_segments(conn)
        if not df.empty:
            # Segment summary cards
            seg_counts = df.groupby("SegmentLabel")["CustomerID"].count().to_dict()
            cols = st.columns(len(seg_counts))
            for i, (label, count) in enumerate(seg_counts.items()):
                color = SEGMENT_COLORS.get(label, "#6B7FA3")
                with cols[i]:
                    st.markdown(f"""
                    <div class='kpi-card' style='--accent-color:{color}'>
                        <div class='kpi-label'>{label}</div>
                        <div class='kpi-value'>{count}</div>
                        <div class='kpi-sub'>customers</div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

            # Segment timeline
            df["SegmentationDate"] = pd.to_datetime(df["SegmentationDate"])
            timeline = df.groupby(["SegmentationDate", "SegmentLabel"]).size().reset_index(name="Count")
            if len(timeline) > 1:
                fig = px.line(timeline, x="SegmentationDate", y="Count",
                              color="SegmentLabel",
                              color_discrete_map=SEGMENT_COLORS)
                fig.update_layout(**PLOTLY_LAYOUT, title="Segment Assignments Over Time",
                                  title_font=dict(color="#E8EEF8", size=13, family="Syne"),
                                  height=200)
                st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
                st.markdown("</div>", unsafe_allow_html=True)

            st.dataframe(df.drop(columns=["CustomerID"]), use_container_width=True, hide_index=True,
                         column_config={
                             "SegmentationID": st.column_config.NumberColumn("ID", width="small"),
                             "ClusterID":      st.column_config.NumberColumn("Cluster", width="small"),
                             "SegmentationDate": st.column_config.DateColumn("Date"),
                         })

    with tab_add:
        st.markdown("<div class='section-title'>Add Segmentation Result</div>", unsafe_allow_html=True)
        df_c = db.get_all_customers(conn)
        segment_labels = ["High-Value Buyers", "Loyal Customers", "At-Risk Customers", "Lost Customers", "New Customers"]
        if df_c.empty:
            st.info("No customers found.")
        else:
            opts = {f"[{r.CustomerID}] {r.FirstName} {r.LastName}": r.CustomerID
                    for _, r in df_c.iterrows()}
            with st.form("add_segment_form", clear_on_submit=True):
                a1, a2, a3, a4 = st.columns(4)
                sel         = a1.selectbox("Customer", list(opts.keys()))
                cluster_id  = a2.number_input("Cluster ID", min_value=0, step=1, value=0)
                label       = a3.selectbox("Segment Label", segment_labels)
                seg_date    = a4.date_input("Segmentation Date", value=date.today())
                if st.form_submit_button("Add Result", type="primary"):
                    cid = opts[sel]
                    ok, new_id = db.add_segment(conn, cid, int(cluster_id), label, seg_date)
                    if ok:
                        st.success(f"Segmentation result {new_id} added ✓")
                        st.rerun()

    with tab_del:
        st.markdown("<div class='section-title'>Delete Segmentation Result</div>", unsafe_allow_html=True)
        df_s = db.get_all_segments(conn)
        if df_s.empty:
            st.info("No segmentation results.")
        else:
            opts = {f"[{r.SegmentationID}] {r.Customer} — {r.SegmentLabel} ({r.SegmentationDate})": r.SegmentationID
                    for _, r in df_s.iterrows()}
            sel = st.selectbox("Select result", list(opts.keys()), key="del_seg")
            sid = opts[sel]
            if st.button("Confirm Delete", type="primary", key="del_seg_btn"):
                ok, _ = db.delete_segment(conn, sid)
                if ok:
                    st.success("Segmentation result deleted ✓")
                    st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: QUERY PACK
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Query Pack":
    st.markdown("""
    <div class='page-hero'>
        <div class='hero-title'>Query Pack</div>
        <div class='hero-sub'>All 15 analytical queries — live results from your database</div>
    </div>
    """, unsafe_allow_html=True)

    # Tier filter
    tier_filter = st.radio("Filter by tier", ["All", "Basic", "Intermediate", "Advanced"],
                           horizontal=True)

    badge_map = {
        "Basic":        "<span class='badge badge-basic'>Basic</span>",
        "Intermediate": "<span class='badge badge-inter'>Intermediate</span>",
        "Advanced":     "<span class='badge badge-advanced'>⭐ Advanced</span>",
    }

    for title, (tier, description, sql) in db.QUERIES.items():
        if tier_filter != "All" and tier != tier_filter:
            continue

        badge = badge_map.get(tier, "")
        with st.expander(f"{title}", expanded=False):
            st.markdown(f"{badge} &nbsp; <span style='font-size:0.84rem;color:#6B7FA3'>{description}</span>",
                        unsafe_allow_html=True)
            st.markdown(f"<div class='sql-block'>{sql.strip()}</div>", unsafe_allow_html=True)

            if st.button(f"▶  Run Query", key=f"run_{title}", type="primary"):
                with st.spinner("Executing..."):
                    result = db.run_query(conn, sql)
                if result.empty:
                    st.info("Query returned no results.")
                else:
                    st.markdown(f"<div class='section-sub'>{len(result)} rows returned</div>",
                                unsafe_allow_html=True)
                    # Format money columns
                    money_cols = [c for c in result.columns
                                  if any(k in c.lower() for k in ["amount","spent","revenue","value","monetary","spending"])]
                    col_config = {c: st.column_config.NumberColumn(c, format="$%.2f") for c in money_cols}
                    st.dataframe(result, use_container_width=True, hide_index=True,
                                 column_config=col_config)
