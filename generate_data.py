"""
Hospitality KPI project - schema + 5-year sample data generator (2021-2025).
Run:  python generate_data.py   ->  creates hotel_kpi.db
Seasonality, pricing, satisfaction and attrition patterns follow the project's
"Seasonal Variations" brief.
"""
import os, sqlite3, uuid, random
from datetime import date, timedelta
import numpy as np
import pandas as pd
from faker import Faker

SEED = 42
rng = np.random.default_rng(SEED)
random.seed(SEED)
Faker.seed(SEED)
DB = "hotel_kpi.db"
START, END = "2021-01-01", "2025-12-31"


def uid():
    return str(uuid.UUID(int=random.getrandbits(128), version=4))


# ------------------------------------------------------------------ config
# monthly occupancy baseline (Jan..Dec) = the seasonality curve of each property
HOTELS = [
    dict(name="Azure Sands Beach Resort", city="Goa", state="Goa", stars=5, rooms=120, adr=9000, kind="leisure",
         season=[.82, .78, .62, .48, .40, .35, .38, .42, .50, .62, .78, .92]),
    dict(name="Lakeview Business Hotel", city="Bengaluru", state="Karnataka", stars=4, rooms=150, adr=6500, kind="business",
         season=[.72, .74, .78, .70, .66, .64, .66, .70, .78, .80, .76, .62]),
    dict(name="Amber Fort Heritage Palace", city="Jaipur", state="Rajasthan", stars=5, rooms=80, adr=11000, kind="leisure",
         season=[.82, .80, .68, .50, .38, .32, .36, .40, .52, .74, .84, .90]),
    dict(name="Marine Drive Grand", city="Mumbai", state="Maharashtra", stars=4, rooms=200, adr=8000, kind="business",
         season=[.74, .72, .70, .66, .64, .55, .52, .56, .64, .72, .76, .82]),
    dict(name="Pine Ridge Hill Retreat", city="Manali", state="Himachal Pradesh", stars=4, rooms=60, adr=6000, kind="leisure",
         season=[.58, .55, .62, .85, .92, .80, .55, .50, .52, .62, .55, .90]),
]
# recovery trend: 2021 = post-COVID trough, steady growth after
YEAR_OCC = {2021: .55, 2022: .80, 2023: .93, 2024: 1.00, 2025: 1.04}
YEAR_RATE = {2021: .88, 2022: .95, 2023: 1.00, 2024: 1.05, 2025: 1.10}
YEAR_ATTR = {2021: 1.3, 2022: 1.5, 2023: 1.1, 2024: .95, 2025: .90}     # attrition multiplier
YEAR_SAT = {2021: -.20, 2022: -.35, 2023: -.10, 2024: .05, 2025: .10}   # service-quality drift
SAT_BASE = {"Goa": 8.4, "Bengaluru": 7.9, "Jaipur": 8.6, "Mumbai": 7.7, "Manali": 8.0}
ROOM_TYPES = [("Standard", 1.0, .60), ("Deluxe", 1.3, .30), ("Suite", 2.0, .10)]
LOS = {"leisure": ([1, 2, 3, 4, 5, 7, 10], [.08, .20, .25, .20, .12, .10, .05]),
       "business": ([1, 2, 3, 4, 5, 7, 10], [.28, .32, .20, .10, .05, .04, .01])}
CHANNELS = {"leisure": (["Direct", "OTA", "Travel Agent", "Corporate"], [.30, .45, .20, .05]),
            "business": (["Direct", "OTA", "Travel Agent", "Corporate"], [.20, .30, .05, .45])}

fk = {c: Faker(l) for c, l in [("India", "en_IN"), ("United States", "en_US"), ("United Kingdom", "en_GB"),
                               ("Germany", "de_DE"), ("France", "fr_FR")]}
COUNTRY_W = [("India", .70), ("United States", .12), ("United Kingdom", .08), ("Germany", .05), ("France", .05)]

DDL = """
CREATE TABLE hotel (hotel_id TEXT PRIMARY KEY, hotel_name TEXT, city TEXT, state TEXT, country TEXT,
                    star_rating INT, total_rooms INT);
CREATE TABLE room (room_id TEXT PRIMARY KEY, hotel_id TEXT REFERENCES hotel(hotel_id), room_number TEXT,
                   room_type TEXT, base_rate REAL);
CREATE TABLE guest (guest_id TEXT PRIMARY KEY, guest_name TEXT, email TEXT, country TEXT, loyalty_tier TEXT);
CREATE TABLE booking (booking_id TEXT PRIMARY KEY, guest_id TEXT REFERENCES guest(guest_id),
                      hotel_id TEXT REFERENCES hotel(hotel_id), room_id TEXT REFERENCES room(room_id),
                      check_in_date TEXT, check_out_date TEXT, nights INT, nightly_rate REAL, room_revenue REAL,
                      channel TEXT, num_guests INT, status TEXT);
CREATE TABLE survey (survey_id TEXT PRIMARY KEY, booking_id TEXT REFERENCES booking(booking_id),
                     hotel_id TEXT REFERENCES hotel(hotel_id), survey_date TEXT, satisfaction_score INT);
CREATE TABLE employee (employee_id TEXT PRIMARY KEY, employee_name TEXT, position TEXT, department TEXT,
                       hotel_id TEXT REFERENCES hotel(hotel_id), employment_type TEXT,
                       hire_date TEXT, termination_date TEXT);
"""


def build():
    if os.path.exists(DB):
        os.remove(DB)
    con = sqlite3.connect(DB)
    con.executescript(DDL)
    days = pd.date_range(START, END)

    # ---------- hotels & rooms
    hotel_rows, room_rows, room_meta = [], [], {}
    for h in HOTELS:
        h["id"] = uid()
        hotel_rows.append((h["id"], h["name"], h["city"], h["state"], "India", h["stars"], h["rooms"]))
        types = rng.choice(len(ROOM_TYPES), h["rooms"], p=[t[2] for t in ROOM_TYPES])
        mult = np.array([ROOM_TYPES[t][1] for t in types])
        ids = [uid() for _ in range(h["rooms"])]
        for i, (rid, t) in enumerate(zip(ids, types)):
            room_rows.append((rid, h["id"], f"{(i // 20) + 1}{(i % 20) + 1:02d}", ROOM_TYPES[t][0],
                              round(h["adr"] * ROOM_TYPES[t][1], -1)))
        room_meta[h["id"]] = (np.array(ids), mult)
    pd.DataFrame(hotel_rows, columns=["hotel_id", "hotel_name", "city", "state", "country", "star_rating", "total_rooms"]
                 ).to_sql("hotel", con, if_exists="append", index=False)
    pd.DataFrame(room_rows, columns=["room_id", "hotel_id", "room_number", "room_type", "base_rate"]
                 ).to_sql("room", con, if_exists="append", index=False)

    # ---------- guests
    G = 45000
    countries = rng.choice([c for c, _ in COUNTRY_W], G, p=[w for _, w in COUNTRY_W])
    tiers = rng.choice(["Bronze", "Silver", "Gold", "Platinum"], G, p=[.60, .25, .12, .03])
    guests = []
    for c, t in zip(countries, tiers):
        name = fk[c].name()
        email = f"{name.lower().replace(' ', '.').replace('..', '.')}{rng.integers(1, 999)}@example.com"
        guests.append((uid(), name, email, c, t))
    gdf = pd.DataFrame(guests, columns=["guest_id", "guest_name", "email", "country", "loyalty_tier"])
    gdf.to_sql("guest", con, if_exists="append", index=False)
    guest_ids = gdf.guest_id.values

    # ---------- bookings (day-by-day occupancy simulation, no double-booked rooms)
    all_b, all_s = [], []
    for h in HOTELS:
        N, base = h["rooms"], np.array(h["season"])
        rel = (base - base.min()) / (base.max() - base.min())
        price_mult = 0.80 + 0.55 * rel                       # off-season -20% ... peak +35%
        rid, rmult = room_meta[h["id"]]
        free = np.zeros(N, dtype=int)
        los_v, los_p = LOS[h["kind"]]
        events = set()
        if h["kind"] == "business":                           # conference / event weeks
            for y in range(2022, 2026):
                for _ in range(3):
                    s = rng.integers(0, 340)
                    events |= {(date(y, 1, 1) + timedelta(days=int(s + k))).toordinal() for k in range(6)}
        rec = []
        for i, d in enumerate(days):
            m, y, dow = d.month - 1, d.year, d.dayofweek
            occ = base[m] * YEAR_OCC[y]
            if y == 2021 and 4 <= d.month <= 6:
                occ *= .60                                    # second COVID wave
            if h["kind"] == "leisure":
                occ *= 1.10 if dow in (4, 5) else .97
            else:
                occ *= 1.08 if dow in (0, 1, 2, 3) else .88
            if d.toordinal() in events:
                occ += .15
            occ = float(min(.97, max(.05, occ * rng.normal(1, .05))))
            need = int(round(occ * N)) - int((free > i).sum())
            if need <= 0:
                continue
            avail = np.flatnonzero(free <= i)
            k = min(need, len(avail))
            pick = rng.choice(avail, k, replace=False)
            los = rng.choice(los_v, k, p=los_p)
            free[pick] = i + los
            rate = h["adr"] * rmult[pick] * price_mult[m] * YEAR_RATE[y] * rng.normal(1, .05, k)
            rec.append(pd.DataFrame({"day": i, "ridx": pick, "nights": los, "rate": np.round(rate, -1), "occ": occ}))
        b = pd.concat(rec, ignore_index=True)
        n = len(b)
        ci = days.values[b.day.values]
        co = ci + b.nights.values.astype("timedelta64[D]")
        ch_v, ch_p = CHANNELS[h["kind"]]
        channel = rng.choice(ch_v, n, p=ch_p)
        rate = b.rate.values * np.where(channel == "Corporate", .90, np.where(channel == "OTA", .97, 1.0))
        rate = np.round(rate, -1)
        bdf = pd.DataFrame({
            "booking_id": [uid() for _ in range(n)], "guest_id": guest_ids[rng.integers(0, G, n)],
            "hotel_id": h["id"], "room_id": rid[b.ridx.values],
            "check_in_date": pd.Series(ci).dt.strftime("%Y-%m-%d").values,
            "check_out_date": pd.Series(co).dt.strftime("%Y-%m-%d").values,
            "nights": b.nights.values, "nightly_rate": rate, "room_revenue": rate * b.nights.values,
            "channel": channel, "num_guests": rng.integers(1, 5, n), "status": "Completed"})
        all_b.append(bdf)
        # surveys: ~40% response; crowding at check-in pulls score down, 2022 staffing crunch too
        mask = rng.random(n) < .40
        yrs = pd.Series(ci).dt.year.values
        eff = -3.0 * np.maximum(0, b.occ.values - .75) + np.array([YEAR_SAT[y] for y in yrs])
        score = np.clip(np.round(SAT_BASE[h["city"]] + eff + rng.normal(0, 1.0, n)), 1, 10).astype(int)
        sd = pd.Series(co + rng.integers(1, 4, n).astype("timedelta64[D]")).dt.strftime("%Y-%m-%d").values
        all_s.append(pd.DataFrame({"survey_id": [uid() for _ in range(mask.sum())],
                                   "booking_id": bdf.booking_id.values[mask], "hotel_id": h["id"],
                                   "survey_date": sd[mask], "satisfaction_score": score[mask]}))
        print(f"  {h['name']}: {n:,} bookings")
    pd.concat(all_b).to_sql("booking", con, if_exists="append", index=False, chunksize=50000)
    pd.concat(all_s).to_sql("survey", con, if_exists="append", index=False, chunksize=50000)

    # ---------- employees (permanent churn + seasonal cohorts)
    POS = [("Front Desk", "Front Desk Agent"), ("Housekeeping", "Room Attendant"), ("Housekeeping", "Housekeeping Supervisor"),
           ("F&B", "Server"), ("F&B", "Chef de Partie"), ("Maintenance", "Technician"), ("Sales", "Sales Executive"),
           ("Management", "Duty Manager")]
    PW = np.array([.17, .30, .05, .20, .10, .08, .05, .05])
    SEAS_POS = [0, 1, 3]
    fin = fk["India"]
    emps = []

    def emp(h, hire, term, kind):
        p = POS[rng.choice(SEAS_POS) if kind == "Seasonal" else rng.choice(len(POS), p=PW)]
        emps.append(dict(employee_id=uid(), employee_name=fin.name(), position=p[1], department=p[0], hotel_id=h["id"],
                         employment_type=kind, hire_date=hire.isoformat(), termination_date=term.isoformat() if term else None))
        return emps[-1]

    def rnd_day(y, m):
        last = (date(y + (m == 12), (m % 12) + 1, 1) - timedelta(days=1)).day
        return date(y, m, int(rng.integers(1, last + 1)))

    for h in HOTELS:
        base = np.array(h["season"]); rel = (base - base.min()) / (base.max() - base.min())
        top = sorted(np.argsort(-base)[:3] + 1)                  # peak months
        groups, cur = [], [top[0]]
        for mth in top[1:]:
            (cur.append(mth) if mth == cur[-1] + 1 else (groups.append(cur), cur := [mth]))
        groups.append(cur)
        active = [emp(h, date(2021, 1, 1) - timedelta(days=int(rng.integers(30, 3000))), None, "Permanent")
                  for _ in range(round(h["rooms"] * .45))]
        pending = 0
        for y in range(2021, 2026):
            for g in groups:                                     # seasonal cohort: hired month before peak, leaves after
                first, last = g[0], g[-1]
                hire = date(y, first, 1) - timedelta(days=30)
                end = (date(y + (last == 12), (last % 12) + 1, 1) - timedelta(days=1))
                for _ in range(round(h["rooms"] * .07 * min(1, YEAR_OCC[y] + .2))):
                    emp(h, hire, end, "Seasonal")
            for m in range(1, 13):
                for _ in range(pending):
                    active.append(emp(h, rnd_day(y, m), None, "Permanent"))
                pending = 0
                p = 0.012 * (1 + .6 * rel[m - 1]) * YEAR_ATTR[y]  # busy season = more stress = more exits
                for e in list(active):
                    if rng.random() < p:
                        e["termination_date"] = rnd_day(y, m).isoformat()
                        active.remove(e)
                        pending += int(rng.random() < .92)
    pd.DataFrame(emps).to_sql("employee", con, if_exists="append", index=False)

    con.executescript("""
        CREATE INDEX ix_b_hotel_in ON booking(hotel_id, check_in_date);
        CREATE INDEX ix_s_hotel ON survey(hotel_id, survey_date);
        CREATE INDEX ix_e_hotel ON employee(hotel_id);
    """)
    con.commit()
    for t in ["hotel", "room", "guest", "booking", "survey", "employee"]:
        print(f"{t:9s}", con.execute(f"select count(*) from {t}").fetchone()[0])
    con.close()


if __name__ == "__main__":
    build()
