-- =====================================================================
-- Aggregate layer for the hospitality KPI dashboard (SQLite dialect)
-- Business logic:
--   * A booking occupies a room for every night in [check_in, check_out)
--   * Rooms available = hotel.total_rooms per night
--   * Occupancy = rooms sold / rooms available ; ADR = revenue / rooms sold ; RevPAR = revenue / rooms available
--   * Turnover = exits in month / average headcount ((start + end)/2) * 100
-- =====================================================================

DROP TABLE IF EXISTS dim_date;
CREATE TABLE dim_date AS
WITH RECURSIVE d(dt) AS (
    SELECT '2021-01-01' UNION ALL SELECT date(dt, '+1 day') FROM d WHERE dt < '2025-12-31')
SELECT dt                                   AS date_key,
       CAST(strftime('%Y', dt) AS INT)      AS year,
       CAST(strftime('%m', dt) AS INT)      AS month,
       strftime('%Y-%m', dt)                AS year_month,
       'Q' || ((CAST(strftime('%m', dt) AS INT) + 2) / 3) AS quarter,
       CAST(strftime('%w', dt) AS INT)      AS dow,            -- 0 = Sunday
       CASE WHEN strftime('%w', dt) IN ('5','6') THEN 1 ELSE 0 END AS is_weekend
FROM d;
CREATE UNIQUE INDEX ix_dim_date ON dim_date(date_key);

DROP TABLE IF EXISTS dim_month;
CREATE TABLE dim_month AS
SELECT strftime('%Y-%m', date_key) AS year_month, date_key AS month_start,
       date(date_key, '+1 month', '-1 day') AS month_end, year, month
FROM dim_date WHERE strftime('%d', date_key) = '01';

-- ---------------------------------------------------------------- daily KPIs
-- (check_in >= date-10d is a pruning predicate: max length of stay is 10 nights)
DROP TABLE IF EXISTS agg_daily_hotel;
CREATE TABLE agg_daily_hotel AS
WITH base AS (
    SELECT d.date_key, d.year, d.month, d.year_month, d.is_weekend,
           h.hotel_id, h.hotel_name, h.city, h.total_rooms AS rooms_available,
           COUNT(b.booking_id)               AS rooms_sold,
           COALESCE(SUM(b.nightly_rate), 0)  AS room_revenue
    FROM dim_date d
    CROSS JOIN hotel h
    LEFT JOIN booking b
           ON b.hotel_id = h.hotel_id
          AND b.status = 'Completed'
          AND b.check_in_date >= date(d.date_key, '-10 days')
          AND b.check_in_date <= d.date_key
          AND b.check_out_date > d.date_key
    GROUP BY d.date_key, h.hotel_id)
SELECT *,
       ROUND(100.0 * rooms_sold / rooms_available, 2)                        AS occupancy_pct,
       ROUND(1.0 * room_revenue / NULLIF(rooms_sold, 0), 2)                  AS adr,
       ROUND(1.0 * room_revenue / rooms_available, 2)                        AS revpar
FROM base;
CREATE INDEX ix_adh ON agg_daily_hotel(hotel_id, year_month);

-- ------------------------------------------------- seasonality classification
-- Each hotel's own calendar months are ranked by average occupancy and split into thirds
DROP TABLE IF EXISTS agg_season_profile;
CREATE TABLE agg_season_profile AS
WITH mo AS (
    SELECT hotel_id, month, AVG(occupancy_pct) AS avg_occ
    FROM agg_daily_hotel WHERE year >= 2023 GROUP BY hotel_id, month)
SELECT hotel_id, month, ROUND(avg_occ, 2) AS avg_occupancy_pct,
       CASE NTILE(3) OVER (PARTITION BY hotel_id ORDER BY avg_occ DESC)
            WHEN 1 THEN 'Peak' WHEN 2 THEN 'Shoulder' ELSE 'Low' END AS season_class
FROM mo;

-- --------------------------------------------------------- monthly hotel KPIs
DROP TABLE IF EXISTS agg_monthly_hotel;
CREATE TABLE agg_monthly_hotel AS
WITH m AS (
    SELECT year_month, year, month, hotel_id, hotel_name, city,
           SUM(rooms_available) AS rooms_available, SUM(rooms_sold) AS rooms_sold, SUM(room_revenue) AS room_revenue
    FROM agg_daily_hotel GROUP BY year_month, hotel_id),
s AS (
    SELECT strftime('%Y-%m', survey_date) AS year_month, hotel_id,
           ROUND(AVG(satisfaction_score), 3) AS guest_satisfaction, COUNT(*) AS survey_count
    FROM survey GROUP BY 1, 2)
SELECT m.*,
       ROUND(100.0 * m.rooms_sold / m.rooms_available, 2)       AS occupancy_pct,
       ROUND(1.0 * m.room_revenue / NULLIF(m.rooms_sold, 0), 2) AS adr,
       ROUND(1.0 * m.room_revenue / m.rooms_available, 2)       AS revpar,
       s.guest_satisfaction, s.survey_count, sp.season_class
FROM m
LEFT JOIN s  ON s.year_month = m.year_month AND s.hotel_id = m.hotel_id
LEFT JOIN agg_season_profile sp ON sp.hotel_id = m.hotel_id AND sp.month = m.month;

-- ------------------------------------------------------------- monthly HR KPIs
DROP TABLE IF EXISTS agg_monthly_hr;
CREATE TABLE agg_monthly_hr AS
WITH x AS (
    SELECT dm.year_month, dm.year, dm.month, e.hotel_id,
           SUM(e.hire_date < dm.month_start AND (e.termination_date IS NULL OR e.termination_date >= dm.month_start)) AS headcount_start,
           SUM(e.hire_date <= dm.month_end  AND (e.termination_date IS NULL OR e.termination_date >  dm.month_end))  AS headcount_end,
           SUM(e.termination_date BETWEEN dm.month_start AND dm.month_end)                                           AS exits,
           SUM(e.termination_date BETWEEN dm.month_start AND dm.month_end AND e.employment_type = 'Seasonal')       AS exits_seasonal,
           SUM(e.hire_date BETWEEN dm.month_start AND dm.month_end)                                                  AS hires
    FROM dim_month dm JOIN employee e ON 1 = 1
    GROUP BY dm.year_month, e.hotel_id)
SELECT x.*, h.hotel_name, h.city,
       ROUND(100.0 * x.exits / NULLIF((x.headcount_start + x.headcount_end) / 2.0, 0), 2) AS turnover_rate_pct
FROM x JOIN hotel h ON h.hotel_id = x.hotel_id;

-- ------------------------------------------------ yearly portfolio roll-up (for headline cards)
DROP TABLE IF EXISTS agg_yearly_portfolio;
CREATE TABLE agg_yearly_portfolio AS
WITH k AS (
    SELECT year, SUM(rooms_available) a, SUM(rooms_sold) s, SUM(room_revenue) r FROM agg_monthly_hotel GROUP BY year),
q AS (SELECT CAST(substr(year_month,1,4) AS INT) year, ROUND(AVG(guest_satisfaction),3) sat FROM agg_monthly_hotel GROUP BY 1),
t AS (
    SELECT year, SUM(exits) AS exits, ROUND(SUM(headcount_start + headcount_end) / 2.0 / 12, 1) AS avg_headcount
    FROM agg_monthly_hr GROUP BY year)
SELECT k.year, ROUND(100.0 * k.s / k.a, 2) AS occupancy_pct, ROUND(1.0 * k.r / k.s, 2) AS adr,
       ROUND(1.0 * k.r / k.a, 2) AS revpar, q.sat AS guest_satisfaction,
       t.exits, t.avg_headcount, ROUND(100.0 * t.exits / t.avg_headcount, 2) AS turnover_rate_pct, k.r AS room_revenue
FROM k JOIN q USING (year) JOIN t USING (year);
