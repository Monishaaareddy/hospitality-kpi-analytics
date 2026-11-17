"""Hospitality KPI dashboard.  Run:  streamlit run app.py
Reads ONLY the aggregate tables built by aggregates.sql."""
import sqlite3
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Hospitality KPI Dashboard", layout="wide")
DB = "hotel_kpi.db"


@st.cache_data
def load(q):
    with sqlite3.connect(DB) as con:
        return pd.read_sql(q, con)


mh = load("SELECT * FROM agg_monthly_hotel")
hr = load("SELECT * FROM agg_monthly_hr")
sp = load("SELECT s.*, h.city FROM agg_season_profile s JOIN hotel h USING(hotel_id)")
mh["date"] = pd.to_datetime(mh.year_month + "-01")
hr["date"] = pd.to_datetime(hr.year_month + "-01")

# ------------------------------------------------------------------ filters
st.title("Hospitality KPI Dashboard  |  2021 - 2025")
with st.sidebar:
    st.header("Filters")
    cities = st.multiselect("Hotels", sorted(mh.city.unique()), default=sorted(mh.city.unique()))
    yr = st.slider("Years", 2021, 2025, (2021, 2025))
    st.caption("Source: aggregate tables agg_monthly_hotel, agg_monthly_hr, agg_season_profile")

f = mh[mh.city.isin(cities) & mh.year.between(*yr)]
fh = hr[hr.city.isin(cities) & hr.year.between(*yr)]
if f.empty:
    st.warning("Select at least one hotel.")
    st.stop()


def portfolio(df):
    g = df.groupby("date").agg(a=("rooms_available", "sum"), s=("rooms_sold", "sum"), r=("room_revenue", "sum"),
                               sat=("guest_satisfaction", "mean")).reset_index()
    g["occupancy_pct"] = 100 * g.s / g.a
    g["adr"] = g.r / g.s
    g["revpar"] = g.r / g.a
    return g


p = portfolio(f)
tot_a, tot_s, tot_r = f.rooms_available.sum(), f.rooms_sold.sum(), f.room_revenue.sum()
exits = fh.exits.sum()
avg_hc = (fh.headcount_start + fh.headcount_end).sum() / 2 / fh.year_month.nunique()
years = max(1, yr[1] - yr[0] + 1)

c = st.columns(5)
c[0].metric("Occupancy", f"{100 * tot_s / tot_a:.1f}%")
c[1].metric("ADR", f"₹{tot_r / tot_s:,.0f}")
c[2].metric("RevPAR", f"₹{tot_r / tot_a:,.0f}")
c[3].metric("Guest satisfaction", f"{f.guest_satisfaction.mean():.2f} / 10")
c[4].metric("Employee turnover (annualised)", f"{100 * exits / avg_hc / years:.1f}%")
st.divider()


def line(df, y, title, ytitle, by_hotel=True):
    fig = px.line(df, x="date", y=y, color="city" if by_hotel else None, title=title,
                  labels={y: ytitle, "date": "", "city": "Hotel"})
    fig.update_layout(legend_orientation="h", legend_y=-0.2, margin=dict(t=50, b=10))
    return fig


by_hotel = st.toggle("Break lines out by hotel", value=True)

# ---------------------------------------------------- KPI 1 + 2: occupancy / ADR
a, b = st.columns(2)
with a:
    st.subheader("1. Occupancy rate")
    st.plotly_chart(line(f if by_hotel else p, "occupancy_pct", "Monthly occupancy %", "Occupancy %", by_hotel),
                    width="stretch")
    hm = f.assign(m=f.date.dt.month).groupby(["city", "m"]).apply(
        lambda d: 100 * d.rooms_sold.sum() / d.rooms_available.sum()).reset_index(name="occ")
    hm = hm.pivot(index="city", columns="m", values="occ")
    hm.columns = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][:len(hm.columns)]
    st.plotly_chart(px.imshow(hm, text_auto=".0f", aspect="auto", color_continuous_scale="YlOrRd",
                              title="Seasonality heatmap: avg occupancy % by calendar month"),
                    width="stretch")
with b:
    st.subheader("2. Average daily rate (ADR)")
    st.plotly_chart(line(f if by_hotel else p, "adr", "Monthly ADR (₹)", "ADR ₹", by_hotel), width="stretch")
    sc = f.groupby(["city", "season_class"]).apply(lambda d: d.room_revenue.sum() / d.rooms_sold.sum()
                                                   ).reset_index(name="adr")
    st.plotly_chart(px.bar(sc, x="city", y="adr", color="season_class", barmode="group",
                           category_orders={"season_class": ["Low", "Shoulder", "Peak"]},
                           title="Peak-season pricing vs off-season discounting", labels={"adr": "ADR ₹", "city": ""}),
                    width="stretch")

# --------------------------------------------------------- KPI 3 + 4: RevPAR / satisfaction
a, b = st.columns(2)
with a:
    st.subheader("3. RevPAR")
    st.plotly_chart(line(f if by_hotel else p, "revpar", "Monthly RevPAR (₹)", "RevPAR ₹", by_hotel),
                    width="stretch")
    yy = f.groupby(["year", "city"]).apply(lambda d: d.room_revenue.sum() / d.rooms_available.sum()).reset_index(name="revpar")
    st.plotly_chart(px.bar(yy, x="year", y="revpar", color="city", barmode="group", title="Annual RevPAR by hotel",
                           labels={"revpar": "RevPAR ₹", "year": ""}), width="stretch")
with b:
    st.subheader("4. Guest satisfaction score")
    st.plotly_chart(line(f if by_hotel else p, "guest_satisfaction" if by_hotel else "sat", "Monthly avg satisfaction (1-10)",
                         "Score", by_hotel), width="stretch")
    st.plotly_chart(px.scatter(f, x="occupancy_pct", y="guest_satisfaction", color="city", opacity=.7,
                               trendline="ols", trendline_scope="overall", trendline_color_override="black",
                               title="Crowding effect: satisfaction vs occupancy",
                               labels={"occupancy_pct": "Occupancy %", "guest_satisfaction": "Satisfaction"}),
                    width="stretch")

# ------------------------------------------------------------------ KPI 5: turnover
st.subheader("5. Employee turnover rate")
a, b = st.columns(2)
t = fh.groupby("date").agg(exits=("exits", "sum"), seas=("exits_seasonal", "sum"),
                           hs=("headcount_start", "sum"), he=("headcount_end", "sum")).reset_index()
t["turnover_pct"] = 100 * t.exits / ((t.hs + t.he) / 2)
t["permanent"] = t.exits - t.seas
with a:
    st.plotly_chart(px.bar(t, x="date", y=["permanent", "seas"], title="Monthly exits: permanent vs seasonal staff",
                           labels={"value": "Exits", "date": "", "variable": ""}), width="stretch")
with b:
    st.plotly_chart(px.line(t, x="date", y="turnover_pct", title="Monthly turnover rate %",
                            labels={"turnover_pct": "Turnover %", "date": ""}), width="stretch")
st.caption("Turnover = exits in month / average headcount x 100. Seasonal cohorts are hired before and released after each hotel's peak months.")
