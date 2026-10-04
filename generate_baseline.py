import csv
import random
from datetime import datetime, timedelta
from pathlib import Path


# ============================================================
# REAL-TIME LOGISTICS CONTROL TOWER
# PHASE 3 BASELINE DATA GENERATOR
# ============================================================
#
# Purpose:
# Reconstruct the frozen Phase 3 baseline according to the
# locked project specification.
#
# Total events:
#   Order events      = 1,000
#   Shipment events   = 4,228
#   Vehicle events    = 5,499
#   Delivery events   = 1,000
#   TOTAL             = 11,727
#
# Fixed seed ensures reproducibility.
# ============================================================


SEED = 42
random.seed(SEED)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

DATA_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# CONFIGURATION
# ============================================================

NUM_ORDERS = 1000
NUM_SHIPMENT_EVENTS = 4228
NUM_VEHICLE_EVENTS = 5499
NUM_DELIVERY_EVENTS = 1000

START_DATE = datetime(2026, 9, 1, 8, 0, 0)


ZONES = [
    "Delhi",
    "Gurgaon",
    "Noida",
    "Ghaziabad",
    "Faridabad",
    "Jaipur",
    "Sonipat",
    "Manesar"
]

WAREHOUSES = [
    "WH001",
    "WH002",
    "WH003",
    "WH004"
]

PRIORITIES = [
    "Standard",
    "Express",
    "High"
]

VEHICLE_STATUSES = [
    "MOVING",
    "IDLE",
    "STOPPED",
    "DELAYED"
]

DELIVERY_STATUSES = [
    "DELIVERED",
    "FAILED"
]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def random_timestamp(start, end):
    """
    Generate a random timestamp between start and end.
    """
    seconds = int((end - start).total_seconds())

    if seconds <= 0:
        return start

    return start + timedelta(
        seconds=random.randint(0, seconds)
    )


def write_csv(filename, fieldnames, rows):
    """
    Write records to CSV.
    """
    path = DATA_DIR / filename

    with open(
        path,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(rows)

    print(
        f"Created {filename}: "
        f"{len(rows):,} records"
    )


# ============================================================
# 1. ORDER EVENTS
# ============================================================

orders = []

for i in range(1, NUM_ORDERS + 1):

    order_id = f"ORD{i:05d}"
    customer_id = f"CUST{random.randint(1, 750):04d}"

    order_timestamp = START_DATE + timedelta(
        minutes=random.randint(
            0,
            60 * 24 * 29
        )
    )

    origin_zone = random.choice(ZONES)

    destination_zone = random.choice(
        [
            zone
            for zone in ZONES
            if zone != origin_zone
        ]
    )

    warehouse_id = random.choice(
        WAREHOUSES
    )

    order_value = round(
        random.uniform(
            1200,
            75000
        ),
        2
    )

    priority = random.choices(
        PRIORITIES,
        weights=[65, 25, 10],
        k=1
    )[0]

    orders.append({
        "order_id": order_id,
        "customer_id": customer_id,
        "order_timestamp": order_timestamp.strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "origin_zone": origin_zone,
        "destination_zone": destination_zone,
        "warehouse_id": warehouse_id,
        "order_value": order_value,
        "priority": priority
    })


# ============================================================
# 2. SHIPMENT EVENTS
# ============================================================

shipment_events = []

shipment_records = []

for i, order in enumerate(orders, start=1):

    shipment_id = f"SHP{i:05d}"

    vehicle_id = f"VH{random.randint(1, 250):03d}"

    order_time = datetime.strptime(
        order["order_timestamp"],
        "%Y-%m-%d %H:%M:%S"
    )

    shipment_created = order_time + timedelta(
        minutes=random.randint(5, 60)
    )

    dispatched = shipment_created + timedelta(
        minutes=random.randint(10, 90)
    )

    in_transit = dispatched + timedelta(
        minutes=random.randint(5, 30)
    )

    zone = order["destination_zone"]

    shipment_records.append({
        "shipment_id": shipment_id,
        "order_id": order["order_id"],
        "warehouse_id": order["warehouse_id"],
        "zone": zone,
        "vehicle_id": vehicle_id,
        "shipment_created": shipment_created,
        "dispatched": dispatched,
        "in_transit": in_transit
    })


# We need exactly 4,228 shipment events.
# Four base events per shipment = 4,000.
# The remaining 228 are additional operational events.

event_counter = 1

for record in shipment_records:

    base_events = [
        (
            record["shipment_created"],
            "SHIPMENT_CREATED"
        ),
        (
            record["dispatched"],
            "DISPATCHED"
        ),
        (
            record["in_transit"],
            "IN_TRANSIT"
        ),
        (
            record["in_transit"] + timedelta(
                minutes=random.randint(5, 45)
            ),
            "VEHICLE_ASSIGNED"
        )
    ]

    for timestamp, event_type in base_events:

        shipment_events.append({
            "event_id": f"SEVT{event_counter:06d}",
            "event_timestamp": timestamp.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "event_type": event_type,
            "shipment_id": record["shipment_id"],
            "order_id": record["order_id"],
            "warehouse_id": record["warehouse_id"],
            "zone": record["zone"],
            "vehicle_id": record["vehicle_id"]
        })

        event_counter += 1


# Add 228 additional shipment operational events.

additional_count = NUM_SHIPMENT_EVENTS - len(
    shipment_events
)

for i in range(additional_count):

    record = random.choice(
        shipment_records
    )

    timestamp = record["in_transit"] + timedelta(
        minutes=random.randint(10, 240)
    )

    event_type = random.choice([
        "IN_TRANSIT",
        "DELAYED",
        "ROUTE_UPDATE"
    ])

    shipment_events.append({
        "event_id": f"SEVT{event_counter:06d}",
        "event_timestamp": timestamp.strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "event_type": event_type,
        "shipment_id": record["shipment_id"],
        "order_id": record["order_id"],
        "warehouse_id": record["warehouse_id"],
        "zone": record["zone"],
        "vehicle_id": record["vehicle_id"]
    })

    event_counter += 1


# ============================================================
# 3. VEHICLE EVENTS
# ============================================================

vehicle_events = []

vehicle_event_counter = 1

for i in range(NUM_VEHICLE_EVENTS):

    record = random.choice(
        shipment_records
    )

    timestamp = record["in_transit"] + timedelta(
        minutes=random.randint(5, 360)
    )

    status = random.choices(
        VEHICLE_STATUSES,
        weights=[65, 12, 13, 10],
        k=1
    )[0]

    if status == "STOPPED":
        speed = 0

    elif status == "DELAYED":
        speed = round(
            random.uniform(5, 20),
            1
        )

    elif status == "IDLE":
        speed = 0

    else:
        speed = round(
            random.uniform(25, 70),
            1
        )

    vehicle_events.append({
        "event_id": f"VEVT{vehicle_event_counter:06d}",
        "event_timestamp": timestamp.strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "event_type": "VEHICLE_STATUS",
        "vehicle_id": record["vehicle_id"],
        "shipment_id": record["shipment_id"],
        "zone": record["zone"],
        "vehicle_status": status,
        "speed_kmh": speed
    })

    vehicle_event_counter += 1


# ============================================================
# 4. DELIVERY EVENTS
# ============================================================

delivery_events = []

delivery_event_counter = 1

for record, order in zip(
    shipment_records,
    orders
):

    # Expected delivery time
    expected_delivery = (
        record["in_transit"]
        + timedelta(
            minutes=random.randint(
                60,
                240
            )
        )
    )

    # Create realistic delivery delay scenarios
    scenario = random.random()

    if scenario < 0.70:
        # Normal delivery
        delay_minutes = random.randint(
            0,
            15
        )

        delivery_status = "DELIVERED"

    elif scenario < 0.92:
        # Delayed delivery
        delay_minutes = random.randint(
            16,
            90
        )

        delivery_status = "DELIVERED"

    elif scenario < 0.97:
        # Severe delay
        delay_minutes = random.randint(
            91,
            240
        )

        delivery_status = "DELIVERED"

    else:
        # Failed delivery
        delay_minutes = random.randint(
            30,
            180
        )

        delivery_status = "FAILED"

    actual_delivery = (
        expected_delivery
        + timedelta(
            minutes=delay_minutes
        )
    )

    delivery_events.append({
        "event_id": f"DEVT{delivery_event_counter:06d}",
        "event_timestamp": actual_delivery.strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "event_type": "DELIVERY_COMPLETED"
        if delivery_status == "DELIVERED"
        else "DELIVERY_FAILED",
        "shipment_id": record["shipment_id"],
        "order_id": order["order_id"],
        "destination_zone": order[
            "destination_zone"
        ],
        "expected_delivery_timestamp":
            expected_delivery.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        "actual_delivery_timestamp":
            actual_delivery.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        "delay_minutes": delay_minutes,
        "delivery_status": delivery_status
    })

    delivery_event_counter += 1


# ============================================================
# 5. WRITE DATASETS
# ============================================================

write_csv(
    "order_events.csv",
    [
        "order_id",
        "customer_id",
        "order_timestamp",
        "origin_zone",
        "destination_zone",
        "warehouse_id",
        "order_value",
        "priority"
    ],
    orders
)


write_csv(
    "shipment_events.csv",
    [
        "event_id",
        "event_timestamp",
        "event_type",
        "shipment_id",
        "order_id",
        "warehouse_id",
        "zone",
        "vehicle_id"
    ],
    shipment_events
)


write_csv(
    "vehicle_events.csv",
    [
        "event_id",
        "event_timestamp",
        "event_type",
        "vehicle_id",
        "shipment_id",
        "zone",
        "vehicle_status",
        "speed_kmh"
    ],
    vehicle_events
)


write_csv(
    "delivery_events.csv",
    [
        "event_id",
        "event_timestamp",
        "event_type",
        "shipment_id",
        "order_id",
        "destination_zone",
        "expected_delivery_timestamp",
        "actual_delivery_timestamp",
        "delay_minutes",
        "delivery_status"
    ],
    delivery_events
)


# ============================================================
# 6. FINAL SUMMARY
# ============================================================

total_events = (
    len(orders)
    + len(shipment_events)
    + len(vehicle_events)
    + len(delivery_events)
)

print("\n" + "=" * 60)
print("PHASE 3 BASELINE DATA GENERATION COMPLETE")
print("=" * 60)

print(
    f"Order events      : {len(orders):,}"
)

print(
    f"Shipment events   : {len(shipment_events):,}"
)

print(
    f"Vehicle events    : {len(vehicle_events):,}"
)

print(
    f"Delivery events   : {len(delivery_events):,}"
)

print(
    f"TOTAL EVENTS      : {total_events:,}"
)

print(
    f"Random seed       : {SEED}"
)

print(
    f"Output directory  : {DATA_DIR}"
)

print("=" * 60)