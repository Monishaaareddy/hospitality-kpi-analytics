# Hospitality KPI Dashboard

End-to-end analytics project for a five-hotel Indian hospitality portfolio: a SQL data model, five years of synthetic sample data (2021-2025), SQL aggregate tables, an interactive dashboard with one panel per KPI, and a written inference report on the seasonal variations.

**Stack:** SQLite · Python (Pandas, NumPy, Faker) · Streamlit + Plotly

## Contents

1. [Project overview](#project-overview)
2. [Headline findings](#headline-findings)
3. [Repository structure](#repository-structure)
4. [Data model](#data-model)
5. [Sample data generation](#sample-data-generation)
6. [SQL aggregate layer](#sql-aggregate-layer)
7. [Dashboard](#dashboard)
8. [How to run](#how-to-run)
9. [Report](#report)
10. [Assumptions and limitations](#assumptions-and-limitations)

## Project overview

The project follows the brief step by step:

| Step | Deliverable | File |
|---|---|---|
| 1 | SQL database with the extended data model | `generate_data.py` (DDL section) |
| 2 | 5 years of sample data in Pandas, UUID keys, realistic names, seasonal trends | `generate_data.py` |
| 3 | SQL aggregate tables with join logic | `aggregates.sql` |
| 4 | Dashboard connected to the aggregate tables, one panel per KPI | `app.py` |
| 5 | Inference document explaining the variations | `report/` |

**KPIs covered:** Occupancy rate, Average Daily Rate (ADR), Revenue per Available Room (RevPAR), Guest satisfaction score, Employee turnover rate.

**The five hotels**

| Hotel | City | Stars | Rooms | Demand profile |
|---|---|---|---|---|
| Azure Sands Beach Resort | Goa | 5 | 120 | Leisure; winter peak, monsoon low |
| Lakeview Business Hotel | Bengaluru | 4 | 150 | Business; weekday-heavy |
| Amber Fort Heritage Palace | Jaipur | 5 | 80 | Leisure; winter peak, summer low |
| Marine Drive Grand | Mumbai | 4 | 200 | Business; weekday-heavy |
| Pine Ridge Hill Retreat | Manali | 4 | 60 | Leisure; Apr-Jun and December peaks |

## Headline findings

- Room revenue grew 2.6x, from Rs 0.65 bn (2021) to Rs 1.66 bn (2025). Occupancy rose from 32.8% to 68.3%, ADR from Rs 8,847 to Rs 10,948.
- Peak months (one third of the calendar) generate 47% of room revenue; low months generate 21%.
- Peak-season RevPAR is 1.7x to 3.5x low-season RevPAR depending on the hotel; leisure hotels are the most seasonal.
- At every hotel, the month with the lowest guest satisfaction is its busiest month.
- Staff turnover spikes in December (12.8%) and January (11.2%) when seasonal cohorts end; permanent-staff exits peaked in 2022, the same year satisfaction was lowest.

The full analysis is in the report (see [Report](#report)).

## Repository structure

```
hotel-kpi-dashboard/
├── generate_data.py        # creates the SQLite schema and generates 5 years of data
├── aggregates.sql          # date dimension + aggregate tables (KPI logic)
├── app.py                  # Streamlit dashboard
├── hotel_kpi_analysis.ipynb# notebook used to query and explore the data
├── hotel_kpi_db.zip        # ready-made database (unzip to get hotel_kpi.db)
├── requirements.txt        # Python dependencies
├── report/                 # inference report (PDF)
├── screenshots/            # dashboard panel screenshots
└── README.md
```

## Data model

The reference model (Hotel, Guest, Employee) was extended so that every KPI can be calculated. All primary keys are UUIDs.

| Table | Purpose | Key columns | Rows |
|---|---|---|---|
| `hotel` | Properties | hotel_id, hotel_name, city, state, star_rating, total_rooms | 5 |
| `room` | Room inventory (needed for occupancy and RevPAR) | room_id, hotel_id, room_type, base_rate | 610 |
| `guest` | Guests | guest_id, guest_name, email, country, loyalty_tier | 45,000 |
| `booking` | Stays (replaces check-in/out on guest; also the Hotel-Guest relationship) | booking_id, guest_id, hotel_id, room_id, check_in_date, check_out_date, nightly_rate, room_revenue, channel | 212,645 |
| `survey` | Guest satisfaction responses | survey_id, booking_id, hotel_id, survey_date, satisfaction_score (1-10) | 84,982 |
| `employee` | Staff (Hotel-Employee relationship) | employee_id, hotel_id, department, position, employment_type, hire_date, termination_date | 1,365 |

Relationships: `room`, `booking`, `survey` and `employee` all reference `hotel`; `booking` references `guest` and `room`; `survey` references `booking`.

## Sample data generation

`generate_data.py` builds the database from scratch with a fixed random seed, so results are reproducible. The trends and variations from the brief are built in:

- **Occupancy seasonality:** each hotel has its own monthly demand curve (for example Goa and Jaipur peak November-February, Manali peaks April-June and December), plus a day-of-week pattern (business hotels fill Sunday-Thursday, leisure hotels fill Friday-Saturday) and conference weeks at the business hotels.
- **Pricing:** ADR rises up to about 35% above base in peak months and falls about 20% below in low months. Suites, Deluxe and Standard rooms carry different rates; Corporate and OTA channels carry small discounts.
- **Multi-year trend:** a post-COVID recovery (2021 trough, second-wave dip in April-June 2021) followed by steady growth, and about 5% a year in rate increases.
- **Guest satisfaction:** scores fall when a hotel is above about 75% occupancy (crowding), and dip in 2021-2022 (service disruption).
- **Turnover:** seasonal staff are hired the month before each hotel's peak months and released afterwards; permanent staff leave at higher rates in busy months and during the 2022 hiring crunch.
- **Realistic names:** guests and employees are generated with Faker using locale-appropriate names (Indian, US, UK, German and French guests).

## SQL aggregate layer

`aggregates.sql` builds these tables, which are the only tables the dashboard reads:

| Table | Grain | Contents |
|---|---|---|
| `dim_date` | Day | Calendar attributes (year, month, quarter, day of week, weekend flag) |
| `dim_month` | Month | Month start and end dates (used for headcount logic) |
| `agg_daily_hotel` | Hotel x day | Rooms available, rooms sold, room revenue, occupancy, ADR, RevPAR |
| `agg_season_profile` | Hotel x calendar month | Average occupancy and a Peak / Shoulder / Low label |
| `agg_monthly_hotel` | Hotel x month | Monthly KPIs, average satisfaction, season class |
| `agg_monthly_hr` | Hotel x month | Headcount start/end, hires, exits (total and seasonal), turnover rate |
| `agg_yearly_portfolio` | Year | Portfolio-level KPIs for headline cards |

**Business logic**

- A booking occupies a room for every night from check-in up to (not including) check-out. `agg_daily_hotel` joins `dim_date` x `hotel` to `booking` on that rule.
- Occupancy = rooms sold / rooms available x 100
- ADR = room revenue / rooms sold
- RevPAR = room revenue / rooms available
- Guest satisfaction = average survey score, by the month the survey was submitted
- Turnover = exits in the period / average of start and end headcount x 100
- Season class: each hotel's 12 calendar months are ranked by average 2023-2025 occupancy and split into thirds (Peak, Shoulder, Low).

## Dashboard

`app.py` is a Streamlit app with a hotel filter, a year-range slider and a toggle between per-hotel lines and a portfolio view. It has headline cards and one panel per KPI:

1. **Occupancy rate:** monthly trend plus a seasonality heatmap by calendar month
2. **ADR:** monthly trend plus peak vs off-season pricing by hotel
3. **RevPAR:** monthly trend plus annual RevPAR by hotel
4. **Guest satisfaction:** monthly trend plus a satisfaction vs occupancy scatter (crowding effect)
5. **Employee turnover:** permanent vs seasonal exits per month plus monthly turnover rate

Screenshots are in `screenshots/`.

## How to run

Requires Python 3.10+.

```bash
# 1. clone and enter the project
git clone <repo-url>
cd hotel-kpi-dashboard

# 2. create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 3. install dependencies
pip install -r requirements.txt

# 4. get the database (either option)
unzip hotel_kpi_db.zip            # option A: use the ready-made database
# or rebuild it from scratch (about 1-2 minutes):
python generate_data.py
python -c "import sqlite3; c = sqlite3.connect('hotel_kpi.db'); c.executescript(open('aggregates.sql').read()); c.commit()"

# 5. launch the dashboard
streamlit run app.py              # opens at http://localhost:8501
```

The notebook `hotel_kpi_analysis.ipynb` can be opened with `jupyter notebook` (install it with `pip install jupyter`). It reads from `hotel_kpi.db` in the project folder.

**Using MySQL or another database:** the tables can be copied from SQLite with pandas and SQLAlchemy (`pip install sqlalchemy pymysql`). The SQLite-specific functions in `aggregates.sql` (`strftime`, `date(x, '+1 day')`) need to be swapped for their MySQL equivalents (`DATE_FORMAT`, `DATE_ADD`).

## Report

The inference report is in `report/`. It covers the project introduction, performance analysis, satisfaction analysis, turnover analysis, seasonal variation analysis, seasonal performance summary, overall findings, business recommendations, and data limitations and assumptions.

## Assumptions and limitations

- **The data is synthetic.** Seasonal curves, price premiums, the crowding effect on satisfaction and attrition rules were built in from the project brief, so the findings illustrate the KPI logic and do not prove causation.
- Five hotels in one country; room revenue only (no F&B, taxes or costs, so no profit measures).
- Every booking is treated as completed: no cancellations, no-shows or overbooking.
- Only about 40% of stays have a satisfaction score, and scores are whole numbers from 1 to 10.
- Turnover is simplified: seasonal cohorts have a fixed size and timing, and there is no voluntary vs involuntary split.
- "Weekend" means Friday and Saturday nights. All money values are nominal Indian rupees.
