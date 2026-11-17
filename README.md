# Hospitality KPI Project (SQLite + Pandas + Streamlit)

    pip install -r requirements.txt
    python generate_data.py                      # schema + 5 yrs sample data -> hotel_kpi.db
    python -c "import sqlite3;c=sqlite3.connect('hotel_kpi.db');c.executescript(open('aggregates.sql').read())"
    streamlit run app.py                         # dashboard

Files: generate_data.py (DDL + generator) | aggregates.sql (dim + aggregate tables) | app.py (dashboard)
Aggregate tables: dim_date, dim_month, agg_daily_hotel, agg_season_profile, agg_monthly_hotel, agg_monthly_hr, agg_yearly_portfolio

Database: unzip hotel_kpi_db.zip to get hotel_kpi.db, or rebuild it with generate_data.py + aggregates.sql.
