# Hospitality KPI Inference Report, 2021–2025

*Portfolio of five Indian hotels (Goa, Bengaluru, Jaipur, Mumbai, Manali) · 610 rooms · 212,645 bookings · 84,982 guest surveys · 1,365 employee records · all figures in INR*

## 1. Introduction to the project

This report analyses five years (2021–2025) of hospitality data for five Indian hotels to explain how occupancy, ADR, RevPAR, guest satisfaction and employee turnover change through the year and across years. Room revenue grew 2.6x, from ₹0.65 bn in 2021 to ₹1.66 bn in 2025, and the hotel-level patterns behind that growth are what the sections below unpack.

**Headline results**

- Portfolio occupancy rose from 32.8% in 2021 to 68.3% in 2025, and ADR rose from ₹8,847 to ₹10,948.
- Peak months are one third of the calendar but produce 47% of room revenue; low months produce 21%.
- At every hotel, the month with the lowest guest satisfaction is its busiest month.
- Staff turnover is dominated by predictable spikes (12.8% in December, 11.2% in January) when seasonal cohorts end.

**The five hotels**

| Hotel | City | Stars | Rooms | Demand profile |
| --- | --- | --- | --- | --- |
| Azure Sands Beach Resort | Goa | 5 | 120 | Leisure; peaks Nov–Feb, monsoon low |
| Lakeview Business Hotel | Bengaluru | 4 | 150 | Business; weekday-heavy, peaks Feb–Mar and Sep–Oct |
| Amber Fort Heritage Palace | Jaipur | 5 | 80 | Leisure; peaks Nov–Feb, summer low |
| Marine Drive Grand | Mumbai | 4 | 200 | Business; weekday-heavy, peaks Nov–Feb |
| Pine Ridge Hill Retreat | Manali | 4 | 60 | Leisure; peaks Apr–Jun and December |

**Data model.** The reference model (Hotel, Guest, Employee) was extended so the KPIs can be calculated: Room (610 rooms), Booking (212,645 stays with check-in, check-out, nightly rate, channel), Survey (84,982 responses, about 40% of stays) and Employee (1,365 records with hire and termination dates). All keys are UUIDs, and guest and employee names are generated with realistic locale-based names. SQL aggregate tables (daily, monthly, HR, season profile, yearly) feed the dashboard.

**KPI definitions**

| KPI | Calculation |
| --- | --- |
| Occupancy rate | Rooms sold ÷ rooms available × 100 |
| ADR | Room revenue ÷ rooms sold |
| RevPAR | Room revenue ÷ rooms available |
| Guest satisfaction | Average survey score (1–10) |
| Employee turnover | Exits in period ÷ average headcount × 100 |

## 2. Performance analysis

Growth came first from occupancy recovery and then from rate: portfolio RevPAR rose 2.6x, from ₹2,901 in 2021 to ₹7,476 in 2025.

| Portfolio KPI | 2021 | 2022 | 2023 | 2024 | 2025 |
| --- | --- | --- | --- | --- | --- |
| Occupancy rate | 32.8% | 52.8% | 61.3% | 65.8% | 68.3% |
| ADR (₹) | 8,847 | 9,444 | 9,936 | 10,457 | 10,948 |
| RevPAR (₹) | 2,901 | 4,986 | 6,087 | 6,880 | 7,476 |
| Room revenue (₹ mn) | 646 | 1,110 | 1,355 | 1,536 | 1,665 |

**Occupancy.** 2021 was the trough, with only 17–21% occupancy in April–June during the second COVID wave. Occupancy then gained 20 points in 2022, 8.5 in 2023, 4.5 in 2024 and 2.5 in 2025. The shrinking gains suggest the portfolio is nearing a ceiling of roughly 70% on current demand.

**ADR.** Rates rose every year, by 6.7% in 2022 and about 5% a year after that, 24% in total since 2021. The first rise reflects the unwinding of 2021 discounting, and later rises reflect steady rate increases.

**RevPAR.** RevPAR combines the two, so its growth is front-loaded: +72% in 2022, +22% in 2023, +13% in 2024 and +9% in 2025. From 2024 onward, rate rather than volume is the main lever.

**Hotel scorecard (2025)**

| Hotel | Occupancy | ADR (₹) | RevPAR (₹) | Room revenue (₹ mn) | Satisfaction |
| --- | --- | --- | --- | --- | --- |
| Jaipur, Amber Fort | 63.1% | 16,062 | 10,127 | 296 | 8.5 |
| Mumbai, Marine Drive | 70.0% | 10,869 | 7,606 | 555 | 7.7 |
| Goa, Azure Sands | 61.3% | 12,399 | 7,602 | 333 | 8.3 |
| Bengaluru, Lakeview | 74.0% | 8,757 | 6,479 | 355 | 7.8 |
| Manali, Pine Ridge | 69.3% | 8,295 | 5,749 | 126 | 7.9 |

- **Jaipur earns the most per room** (₹10,127 RevPAR) on only 63% occupancy, because its ADR is almost double that of Bengaluru or Manali.
- **Mumbai earns the most in total** (₹555 mn) because it has 200 rooms, while its RevPAR is mid-table.
- **Bengaluru has the highest occupancy** (74%) but a low ADR, so it is the clearest candidate for pushing rates.
- **Goa has the most headroom**, with 61% occupancy for a 5-star resort.

**Room type, channel and stay length.** Suites sell at about ₹16,500 on average against ₹8,300 for Standard rooms. Leisure hotels average 3.8 nights per stay against 2.6 at the business hotels. Corporate bookings carry the lowest average rate (₹8,788) and travel-agent bookings the highest (₹10,967), though part of that gap is hotel mix, because corporate demand sits mostly in Bengaluru and Mumbai.

## 3. Satisfaction analysis

Guests are broadly satisfied, with a portfolio average of 7.8–8.1 out of 10 in every year, but scores fall when hotels are full and when staffing is unstable.

**Score levels.** About 62% of survey responses are 8 or higher (8 is the most common score at 36%, followed by 7 at 28% and 9 at 20%), and about 11% are 6 or lower. The portfolio average dipped to 7.77 in 2022, recovered to 7.97 in 2023 and reached 8.07 in 2024 and 2025.

**By hotel.** The two 5-star hotels lead: Jaipur averages 8.4 and Goa 8.2 across the five years, against 7.8 for Manali, 7.7 for Bengaluru and 7.6 for Mumbai. The business hotels score lowest, and corporate bookings (7.67) trail travel-agent bookings (7.99), largely because corporate demand sits at those hotels. Satisfaction is identical across loyalty tiers (7.81), so loyalty status is not a driver here.

**The crowding effect.** Every hotel scores lower in its peak months than in its low months (2023–25 averages):

| Hotel | Low season | Peak season | Change |
| --- | --- | --- | --- |
| Jaipur | 8.6 | 8.3 | −0.3 |
| Goa | 8.4 | 8.1 | −0.3 |
| Manali | 8.0 | 7.7 | −0.3 |
| Bengaluru | 7.9 | 7.7 | −0.2 |
| Mumbai | 7.7 | 7.6 | −0.1 |

The lowest-scoring month at each hotel is also its highest-occupancy month: December for Goa, Jaipur and Mumbai, May for Manali and October for Bengaluru. Hotel-months at 80% occupancy or more averaged 7.95 against 8.06 below that level, and across 2023–25 hotel-months the correlation between occupancy and satisfaction is about −0.49. The likely mechanisms are those named in the brief: crowded spaces, longer waits and less personal attention.

**Service drift.** Satisfaction was also weak in 2021–2022 (7.92 and 7.77) even though occupancy was low. 2022 is the year with the most permanent-staff exits, so staffing disruption, not crowding, explains the dip. Scores recovered as exits fell.

## 4. Turnover analysis

Blended turnover runs at about 45–57% a year, but most of it is planned seasonal departures; the number to watch is permanent-staff exits, which fell from 70 in 2022 to 41 in 2025.

| Year | Total exits | Seasonal exits | Permanent exits | Blended turnover |
| --- | --- | --- | --- | --- |
| 2021 | 125 | 64 | 61 | 45.1% |
| 2022 | 156 | 86 | 70 | 57.2% |
| 2023 | 133 | 86 | 47 | 49.1% |
| 2024 | 139 | 86 | 53 | 51.9% |
| 2025 | 127 | 86 | 41 | 48.8% |

Average headcount stayed between 261 and 277 across the portfolio. Turnover is exits in the year divided by average headcount.

**Seasonal spikes.** Hotels hire extra staff before their peak months and release them after. Monthly turnover is therefore only 1–2% in most months but jumps in the months when cohorts end: 12.8% in December, 11.2% in January, 6.0% in October, 5.3% in March and 3.4% in May. These spikes are structural and predictable, not a sign of trouble.

**Permanent staff and stress.** Permanent exits peaked at 70 in 2022 during the post-COVID hiring competition and then fell by 41% to 41 in 2025. In peak-season months, permanent staff leave at about 1.96% a month against 1.35% in low-season months, roughly 45% higher, which is consistent with heavier workload and burnout when hotels are full.

**By hotel (2021–2025)**

| Hotel | Total exits | Of which seasonal | Blended annual turnover |
| --- | --- | --- | --- |
| Mumbai | 218 | 134 | 48.9% |
| Bengaluru | 175 | 104 | 53.5% |
| Goa | 126 | 76 | 48.9% |
| Jaipur | 91 | 56 | 50.2% |
| Manali | 70 | 38 | 51.3% |

Rates are similar across hotels (49–54%), so the differences in exit counts mostly reflect hotel size.

**By department.** Three frontline departments account for 628 of the 680 exits (92%): Housekeeping (224), F&B (225) and Front Desk (179). Seasonal hires are placed only in those departments, which partly explains the concentration. Management (9 exits) and Sales (11) are the most stable.

**Link to guest experience.** 2022 combined the most permanent exits with the lowest guest satisfaction (7.77). As permanent exits fell, satisfaction rose to 8.07.

## 5. Seasonal variation analysis

Every hotel has a distinct demand calendar, and the leisure resorts swing far more than the business hotels: Goa and Jaipur move 55–57 occupancy points between their best and worst months, Bengaluru only 18.

Each hotel's calendar months were ranked by average occupancy (2023–2025) and split into thirds: four Peak, four Shoulder and four Low months.

| Hotel | Peak months | Shoulder months | Low months | Best month | Worst month |
| --- | --- | --- | --- | --- | --- |
| Goa | Nov, Dec, Jan, Feb | Mar, Apr, Sep, Oct | May–Aug | Dec, 90.0% | Jun, 35.2% |
| Jaipur | Nov, Dec, Jan, Feb | Mar, Apr, Sep, Oct | May–Aug | Dec, 88.8% | Jun, 31.7% |
| Manali | Apr, May, Jun, Dec | Jan, Mar, Oct, Nov | Feb, Jul, Aug, Sep | May, 90.3% | Aug, 50.3% |
| Mumbai | Nov, Dec, Jan, Feb | Mar, Apr, May, Oct | Jun–Sep | Dec, 81.1% | Jul, 53.0% |
| Bengaluru | Feb, Mar, Sep, Oct | Jan, Apr, Aug, Nov | May, Jun, Jul, Dec | Oct, 79.2% | Dec, 61.2% |

**Seasonal tourism.** Goa and Jaipur fill with winter holiday travel and empty in the monsoon and summer heat. Manali is the inverse: it peaks in April–June when the plains are hot, and again in December, and softens in July–September. Leisure guests also stay longer (3.8 nights on average against 2.6 for business hotels), which lifts peak-season room-nights.

**Events and conferences.** The business hotels add about 15 occupancy points during conference and event weeks. Event weeks fall at different times each year, so they add short spikes on top of the seasonal pattern.

**Business travel calendar.** Bengaluru drops to 61% in December as corporate travel slows at year end, its weakest month despite being a holiday month elsewhere.

**Day-of-week pattern.** Business hotels fill from Sunday to Thursday and leisure hotels on Friday and Saturday nights (2023–25 average occupancy):

| Hotel | Type | Sun–Thu | Fri–Sat |
| --- | --- | --- | --- |
| Bengaluru | Business | 73.9% | 62.9% |
| Mumbai | Business | 69.4% | 58.9% |
| Goa | Leisure | 56.7% | 63.7% |
| Jaipur | Leisure | 58.0% | 65.4% |
| Manali | Leisure | 64.0% | 71.6% |

**Pricing and staffing follow the calendar.** Rates are raised in each hotel's peak months and discounted in its low months, so ADR and occupancy rise together. Seasonal staff are hired the month before peak and released after it, which drives the turnover spikes in section 4.

## 6. Seasonal performance summary

Peak months earn 2.3x the RevPAR of low months and produce 47% of room revenue from one third of the calendar, at the price of slightly lower guest satisfaction.

**Portfolio by season class (2021–2025)**

| Season | Occupancy | ADR (₹) | RevPAR (₹) | Room revenue (₹ mn) | Share of revenue | Satisfaction |
| --- | --- | --- | --- | --- | --- | --- |
| Peak | 68.9% | 11,776 | 8,108 | 2,977 | 47.2% | 7.87 |
| Shoulder | 55.5% | 9,840 | 5,461 | 2,039 | 32.3% | 7.98 |
| Low | 44.4% | 7,813 | 3,471 | 1,296 | 20.5% | 8.02 |

These averages include 2021, so the gaps are understated. Using 2023–2025 only, satisfaction is 7.90 in peak months against 8.14 in low months.

**Peak vs low season by hotel (2023–2025)**

| Hotel | Occupancy, low → peak | ADR (₹), low → peak | RevPAR (₹), low → peak | RevPAR multiple |
| --- | --- | --- | --- | --- |
| Jaipur | 36.5% → 83.6% | 11,402 → 17,499 | 4,157 → 14,632 | 3.5x |
| Goa | 38.9% → 82.1% | 9,154 → 13,745 | 3,557 → 11,291 | 3.2x |
| Manali | 53.0% → 86.1% | 6,364 → 9,560 | 3,370 → 8,233 | 2.4x |
| Mumbai | 56.8% → 74.9% | 8,470 → 11,831 | 4,810 → 8,859 | 1.8x |
| Bengaluru | 64.0% → 77.3% | 6,738 → 9,689 | 4,311 → 7,489 | 1.7x |

- **Leisure hotels are the most seasonal.** Jaipur and Goa earn about three times more RevPAR per room in peak than in low months, because occupancy more than doubles and ADR rises by about half.
- **Business hotels are the most stable.** Bengaluru and Mumbai earn 1.7–1.8x, with a high low-season floor of 57–64% occupancy.
- **Rate premiums are similar everywhere.** Peak ADR is 40–54% above low-season ADR at every hotel, so the difference between hotels comes mainly from occupancy.

**Calendar view (2025).** December was the strongest month for the portfolio, with 83.8% occupancy and ₹10,862 RevPAR. July was the weakest, with 52.9% and ₹4,367, a 2.5x gap.

## 7. Overall seasonal findings

Seasonality is the largest force in the data: demand sets occupancy, occupancy allows higher rates, and the same peak pressure lowers guest satisfaction and increases staff exits.

1. **Demand calendars differ by hotel type.** Leisure hotels swing 40–57 occupancy points between best and worst month; business hotels swing 18–28.
2. **Revenue is concentrated in peak months.** The four peak months at each hotel generate 47% of room revenue, and the four low months only 21%.
3. **Price follows demand.** Peak ADR is 40–54% above low-season ADR at every hotel, so rate and occupancy reinforce each other and RevPAR swings more than either.
4. **Volume drove the recovery; rate drives growth now.** Occupancy gains shrank from 20 points in 2022 to 2.5 in 2025, while ADR kept rising about 5% a year.
5. **Full hotels disappoint more guests.** At all five hotels, the lowest-satisfaction month is the highest-occupancy month, with peak-season scores 0.1–0.3 points below low-season scores.
6. **Turnover has a planned and an unplanned part.** Seasonal exits create predictable spikes in December, January, October and March, while permanent exits run about 45% higher in peak months.
7. **Staffing and satisfaction move together.** 2022 had the most permanent exits and the lowest satisfaction; both improved after.

**How the KPIs connect.** The most profitable months are also the riskiest. Peak demand lifts occupancy, ADR and RevPAR together, but it also crowds the property, adds workload for permanent staff and raises their exit rate. Higher attrition then weakens service the following season, which pulls satisfaction down. Growth that ignores this loop risks trading short-term revenue for guest experience and retention.

## 8. Key business recommendations

Occupancy is nearing its ceiling, so the biggest gains are in rate, in protecting peak-season service and staff, and in filling the quiet months and quiet days.

1. **Lift rates where occupancy is already high.** Bengaluru runs 74% occupancy at the lowest ADR in the portfolio outside Manali (₹8,757), and Manali is at 69%. Test rate increases in their months above 70% occupancy before adding more volume.
2. **Protect service in peak months.** Hotel-months at 80% occupancy or more score 7.95 against 8.06 below that level, and peak scores are 0.1–0.3 points lower at every hotel. Add rostered staff and a surge plan for peak weeks, and limit sell-out of the last rooms when service capacity is thin.
3. **Retain permanent staff before the peak.** Permanent exits run about 45% higher in peak months, and the 2022 spike coincided with the weakest guest scores. Time retention bonuses, leave planning and rota relief to land ahead of each hotel's peak months.
4. **Build a returning seasonal pool.** Each year about 86 seasonal staff are hired and released, all in Housekeeping, F&B and Front Desk, which also hold 92% of exits. Re-hire alumni first, shorten onboarding and cross-train across the three departments.
5. **Fill the low season at the leisure hotels.** Goa and Jaipur sit at 37–39% occupancy in their low months against 82–84% at peak. Target monsoon and summer packages, domestic staycations and mid-week corporate offsites, rather than deeper discounts.
6. **Fill the quiet days.** Bengaluru and Mumbai fall to 59–63% on Friday and Saturday nights, so leisure packages suit them. Goa, Jaipur and Manali are weakest from Sunday to Thursday, so mid-week offers suit them.
7. **Create a year-end draw for Bengaluru.** December is its weakest month at 61% as corporate travel slows. Events, festive packages and conference blocks could lift it.
8. **Track early-warning thresholds on the dashboard.** Suggested triggers: occupancy above 85%, monthly satisfaction below 7.8, and permanent-staff turnover above 2% a month.

**Next analysis steps.** Adding cost data would allow profit measures such as GOPPAR, and cancellation and guest-comment data would explain satisfaction drivers beyond occupancy.

## 9. Data limitations and assumptions

The findings show how the KPIs behave under the seasonal logic in the brief, not how a real portfolio performed, so they should be read as a worked example.

**Limitations**

- **Synthetic data.** The seasonal curves, price premiums, crowding penalty on satisfaction and attrition rules were built into the generator from the project brief. Relationships such as the occupancy–satisfaction correlation (about −0.49) are therefore partly by design and do not prove causation.
- **Small, single-country portfolio.** Five hotels and 610 rooms in India, with no international seasonality or competitor data.
- **Room revenue only.** F&B, spa, taxes and all costs are excluded, so profit measures such as GOPPAR cannot be calculated.
- **Simplified bookings.** Every stay is marked Completed: no cancellations, no-shows or overbooking. One room holds one stay at a time, and stays run from 1 to 10 nights.
- **Survey bias.** Only about 40% of stays have a score, scores are whole numbers from 1 to 10, and a survey is dated 1–3 days after check-out, so monthly scores lag stays slightly. There are no free-text comments.
- **No effect from loyalty tier or channel.** The data has no built-in link between those fields and satisfaction, so it cannot test them.
- **Turnover is simplified.** Seasonal cohorts have a fixed size and timing, permanent exits are random with seasonal and yearly multipliers, and there is no split between voluntary and involuntary exits.

**Assumptions**

- Occupied rooms for a night = bookings with check-in on or before that night and check-out after it. Rooms available = total rooms of the hotel.
- A year-by-year recovery was assumed after 2021 (occupancy factors of 0.55, 0.80, 0.93, 1.00 and 1.04 of each hotel's base), plus a second COVID-wave dip in April–June 2021.
- Season classes (Peak, Shoulder, Low) split each hotel's calendar months into thirds by average 2023–2025 occupancy. Averages that include 2021 understate seasonal gaps.
- "Fri–Sat" nights are treated as the weekend in the date dimension.
- All money values are nominal Indian rupees, not adjusted for inflation.
- Turnover = exits ÷ average of start and end headcount for the period. Annual figures sum the monthly exits and use the average monthly headcount.
