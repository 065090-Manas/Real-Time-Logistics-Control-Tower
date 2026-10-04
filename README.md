# Real-Time Logistics Control Tower

Kafka-based streaming analytics that detects shipment delays and risks as they happen, quantifies the value exposed, and ranks what to fix first.

**Stack:** Apache Kafka · Python · MySQL · Grafana · Docker

**Team:** Manas Gupta · Sneha Umar Vaishya · Aditya Mishra  
**Submitted to:** Prof. Aditya Dua

---

## Problem

Logistics operations generate order, shipment, vehicle and delivery events all day, but delays usually surface only in end-of-day reports, after the customer has felt them. A shipment 30 minutes late at 10 a.m. can still be recovered; by evening it can only be recorded.

**Core question:** How can real-time streaming analytics identify shipment delays and operational risks early enough to intervene?

## Solution

```
Logistics Events → Python Producers → Apache Kafka → Python Stream Processor
                 → Risk Engine → MySQL → Grafana Control Tower → Action
```

Decision framework: **Detect → Diagnose → Quantify → Prioritise → Act**

![Architecture](End_to_End_Infrastructure.png)

## Key Results

| Metric | Value |
|---|---|
| Events streamed | 11,727 (0 invalid, 0 duplicate) |
| On-time delivery | 4.90% |
| Average delay | 29.93 min (max 238 min) |
| Orders at risk | 344 |
| Critical orders | 225 |
| Order value at risk | ₹12.78 million |
| Automated tests | 19/19 processing, 29/29 MySQL |

**Zone insights:** Jaipur has the highest average delay (32.54 min), Noida the highest risk rate (45.71%), Ghaziabad the lowest on-time rate (3.10%).

## Data

| Stream | Events | Kafka topic | Key |
|---|---|---|---|
| Orders | 1,000 | `order_events` | `order_id` |
| Shipments | 4,228 | `shipment_events` | `shipment_id` |
| Vehicles | 5,499 | `vehicle_events` | `vehicle_id` |
| Deliveries | 1,000 | `delivery_events` | `shipment_id` |

Each topic: 3 partitions, replication factor 1, broker at `localhost:9092`.

## Risk Engine

| Level | Rule |
|---|---|
| LOW | Delay ≤ 15 min |
| MEDIUM | Delay > 15 min |
| HIGH | Delay > 30 min |
| CRITICAL | Delay > 60 min or failed delivery |

Vehicle status, shipment priority and express shipping can raise the score further.

## Dashboard

- Executive KPIs, delivery trend, shipment status, performance by zone
- Exception Center: top 30 intervention candidates (P1 to P5)
- Business impact: critical orders, average delay, order value at risk
- Filters: **Zone · Risk · Priority · Vehicle Status**  
  Example: `Gurgaon + CRITICAL + Express + STOPPED`

## Project Structure

```
Real_Time_Logistics_Control_Tower/
├── data/                  # 4 baseline CSV files
├── producers/             # order, shipment, vehicle, delivery producers
├── stream_processor/      # consumer.py, config.py, README
├── generate_baseline.py
└── validate_baseline.py
```

MySQL: database `logistics_control_tower`, table `logistics_analytics`, six views (`vw_executive_kpis`, `vw_zone_performance`, `vw_risk_distribution`, `vw_priority_risk`, `vw_delay_performance`, `vw_intervention_candidates`).

## Run It

1. Start Kafka, Zookeeper and MySQL with Docker Compose.
2. Validate the baseline: `python validate_baseline.py`
3. Run the four producers to stream all 11,727 events.
4. Run `stream_processor/consumer.py` to validate, enrich, compute KPIs and score risk.
5. Load the analytical dataset into MySQL and create the SQL views.
6. Connect Grafana to MySQL and open the Logistics Control Tower dashboard.

**Environment:** Windows, PowerShell, VS Code, Python 3.14.6, Docker 29.6.1, kafka-python 3.0.9.

## Limitations and Roadmap

**Limits:** prepared dataset (no live enterprise data), rule-based risk, no GPS integration, single local Kafka broker.

**Next:** automated CRITICAL alerts and zone-specific thresholds → live GPS and ML delay prediction → route optimisation and multi-broker Kafka.
