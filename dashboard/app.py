
from __future__ import annotations

from datetime import timedelta

import pandas as pd
import plotly.express as px
import streamlit as st

from utils_db import (
    available_report_dates,
    browser_os_views_by_hour,
    fetch_kpis,
    list_countries,
    list_products,
    product_views_by_hour,
    stores_by_country,
    top10_countries_today,
    top10_products_today,
    top5_referrers_today,
)

st.set_page_config(
    page_title="Glamira View Reports",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600&family=Source+Sans+3:wght@400;500;600&display=swap');
      :root {
        --ink: #0f1419; --line: #2a3340; --gold: #c4a574; --muted: #9aa7b5; --text: #e8eef4;
      }
      html, body, [class*="css"] { font-family: "Source Sans 3", sans-serif; color: var(--text); }
      .stApp {
        background:
          radial-gradient(1100px 520px at 8% -12%, #1c2836 0%, transparent 55%),
          radial-gradient(800px 460px at 100% 0%, #24301f 0%, transparent 45%),
          var(--ink);
      }
      .brand {
        font-family: "Cormorant Garamond", serif;
        font-size: 2.8rem; letter-spacing: 0.08em; color: var(--gold);
        margin: 0; line-height: 1;
      }
      .tagline { color: var(--muted); margin: 0.35rem 0 1.1rem; }
      .kpi {
        background: linear-gradient(180deg, #1b232c 0%, #141a21 100%);
        border: 1px solid var(--line); border-radius: 10px; padding: 0.9rem 1rem;
      }
      .kpi .label { color: var(--muted); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em; }
      .kpi .value { font-family: "Cormorant Garamond", serif; font-size: 2rem; margin-top: 0.15rem; }
      h2, h3, h4 { font-family: "Cormorant Garamond", serif !important; color: var(--gold) !important; }
      #MainMenu, footer { visibility: hidden; }
      header { background: transparent !important; }
    </style>
    """,
    unsafe_allow_html=True,
)


def _fmt(n) -> str:
    try:
        return f"{int(n):,}"
    except Exception:
        return "—"


def _layout(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e8eef4",
        margin=dict(l=10, r=10, t=36, b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
    fig.update_xaxes(gridcolor="#2a3340", zeroline=False)
    fig.update_yaxes(gridcolor="#2a3340", zeroline=False)
    return fig


st.markdown('<p class="brand">GLAMIRA</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="tagline">Báo cáo product view realtime · Spark → PostgreSQL</p>',
    unsafe_allow_html=True,
)


@st.fragment(run_every=timedelta(seconds=8))
def reports():
    try:
        dates = available_report_dates()
    except Exception as e:
        st.error(f"Không kết nối được Postgres: {e}")
        st.caption("Host: POSTGRES_HOST=localhost POSTGRES_PORT=5433")
        return

    if not dates:
        st.warning("Chưa có dữ liệu trong fact_product_view. Hãy chạy Spark streaming trước.")
        return

    with st.sidebar:
        st.markdown("### Bộ lọc")
        report_date = st.selectbox("Ngày báo cáo", dates, index=0, format_func=lambda d: str(d))
        countries = list_countries(report_date) or ["Unknown"]
        country = st.selectbox("Quốc gia (báo cáo 4)", countries, index=0)
        products = list_products(report_date) or []
        product_id = st.selectbox(
            "Product ID (báo cáo 5)",
            products if products else ["(none)"],
            index=0,
        )
        st.caption("Dashboard tự refresh mỗi 8 giây.")

    kpis = fetch_kpis(report_date)
    k1, k2, k3, k4 = st.columns(4)
    for col, label, value in [
        (k1, "Views trong ngày", kpis.get("views_today")),
        (k2, "Products", kpis.get("products_today")),
        (k3, "Stores", kpis.get("stores_today")),
        (k4, "Countries (domain)", kpis.get("countries_today")),
    ]:
        with col:
            st.markdown(
                f'<div class="kpi"><div class="label">{label}</div>'
                f'<div class="value">{_fmt(value)}</div></div>',
                unsafe_allow_html=True,
            )
    st.caption(f"Last event: {kpis.get('last_event_at') or '—'} · ngày {report_date}")

    # ----- Report 1 & 2 -----
    r1, r2 = st.columns(2)
    with r1:
        st.subheader("1. Top 10 product_id (views hôm nay)")
        top_products = top10_products_today(report_date)
        if top_products.empty:
            st.info("Không có product view trong ngày này.")
        else:
            fig = px.bar(
                top_products.sort_values("views"),
                x="views",
                y="product_id",
                orientation="h",
                color_discrete_sequence=["#c4a574"],
            )
            st.plotly_chart(_layout(fig), use_container_width=True, config={"displayModeBar": False})
            st.dataframe(top_products, use_container_width=True, hide_index=True)

    with r2:
        st.subheader("2. Top 10 quốc gia theo domain")
        top_countries = top10_countries_today(report_date)
        if top_countries.empty:
            st.info(
                "Chưa có `country_domain`. Restart Spark sau khi migrate cột "
                "(sql/migrate_fact_report_cols.sql)."
            )
        else:
            fig = px.bar(
                top_countries.sort_values("views"),
                x="views",
                y="country",
                orientation="h",
                color_discrete_sequence=["#8fa38a"],
            )
            st.plotly_chart(_layout(fig), use_container_width=True, config={"displayModeBar": False})
            st.dataframe(top_countries, use_container_width=True, hide_index=True)

    # ----- Report 3 -----
    st.subheader("3. Top 5 referrer_url (views hôm nay)")
    top_ref = top5_referrers_today(report_date)
    if top_ref.empty:
        st.info("Chưa có referrer_url trong ngày này.")
    else:
        st.dataframe(top_ref, use_container_width=True, hide_index=True)

    # ----- Report 4 -----
    st.subheader(f"4. Store theo quốc gia: {country}")
    stores = stores_by_country(report_date, country)
    if stores.empty:
        st.info("Không có store cho quốc gia này.")
    else:
        c4a, c4b = st.columns([1.4, 1])
        with c4a:
            fig = px.bar(
                stores.head(20).sort_values("views"),
                x="views",
                y="store_id",
                orientation="h",
                color_discrete_sequence=["#6f8fad"],
            )
            st.plotly_chart(_layout(fig), use_container_width=True, config={"displayModeBar": False})
        with c4b:
            st.dataframe(stores, use_container_width=True, hide_index=True)

    # ----- Report 5 -----
    st.subheader(f"5. Views theo giờ · product `{product_id}`")
    if not products or product_id == "(none)":
        st.info("Chưa có product_id để chọn.")
    else:
        by_hour = product_views_by_hour(report_date, product_id)
        # fill missing hours 0-23
        full = pd.DataFrame({"hour": list(range(24))}).merge(by_hour, on="hour", how="left").fillna({"views": 0})
        fig = px.bar(full, x="hour", y="views", color_discrete_sequence=["#c4a574"])
        fig.update_xaxes(dtick=1)
        st.plotly_chart(_layout(fig), use_container_width=True, config={"displayModeBar": False})

    # ----- Report 6 -----
    st.subheader("6. Views theo giờ · Browser / OS")
    bos = browser_os_views_by_hour(report_date)
    if bos.empty:
        st.info(
            "Chưa có browser/os. Restart Spark sau migrate "
            "(cần `user-agents` + PYSPARK_PYTHON conda)."
        )
    else:
        bos["browser_os"] = bos["browser"].astype(str) + " / " + bos["os"].astype(str)
        top_pairs = (
            bos.groupby("browser_os", as_index=False)["views"]
            .sum()
            .sort_values("views", ascending=False)
            .head(8)["browser_os"]
            .tolist()
        )
        plot_df = bos[bos["browser_os"].isin(top_pairs)]
        fig = px.line(
            plot_df,
            x="hour",
            y="views",
            color="browser_os",
            markers=True,
        )
        fig.update_xaxes(dtick=1)
        st.plotly_chart(_layout(fig), use_container_width=True, config={"displayModeBar": False})
        st.dataframe(
            bos.sort_values(["hour", "views"], ascending=[True, False]),
            use_container_width=True,
            hide_index=True,
        )


reports()
