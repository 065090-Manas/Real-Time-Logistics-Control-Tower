import csv
from pathlib import Path
from datetime import datetime


# ============================================================
# REAL-TIME LOGISTICS CONTROL TOWER
# PHASE 3 BASELINE VALIDATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


# ============================================================
# EXPECTED DATASET VOLUMES
# ============================================================

EXPECTED_COUNTS = {
    "order_events.csv": 1000,
    "shipment_events.csv": 4228,
    "vehicle_events.csv": 5499,
    "delivery_events.csv": 1000
}


EXPECTED_TOTAL_EVENTS = 11727


# ============================================================
# EXPECTED COLUMN STRUCTURES
# ============================================================

EXPECTED_COLUMNS = {

    "order_events.csv": [
        "order_id",
        "customer_id",
        "order_timestamp",
        "origin_zone",
        "destination_zone",
        "warehouse_id",
        "order_value",
        "priority"
    ],

    "shipment_events.csv": [
        "event_id",
        "event_timestamp",
        "event_type",
        "shipment_id",
        "order_id",
        "warehouse_id",
        "zone",
        "vehicle_id"
    ],

    "vehicle_events.csv": [
        "event_id",
        "event_timestamp",
        "event_type",
        "vehicle_id",
        "shipment_id",
        "zone",
        "vehicle_status",
        "speed_kmh"
    ],

    "delivery_events.csv": [
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
    ]
}


# ============================================================
# VALID VALUES
# ============================================================

VALID_PRIORITIES = {
    "Standard",
    "Express",
    "High"
}

VALID_VEHICLE_STATUSES = {
    "MOVING",
    "IDLE",
    "STOPPED",
    "DELAYED"
}

VALID_DELIVERY_STATUSES = {
    "DELIVERED",
    "FAILED"
}


# ============================================================
# ISSUE TRACKER
# ============================================================

issues = []


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def read_csv(filename):

    path = DATA_DIR / filename

    if not path.exists():

        issues.append(
            f"Missing file: {filename}"
        )

        return []

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return list(
            csv.DictReader(file)
        )


def parse_timestamp(value):

    return datetime.strptime(
        value,
        "%Y-%m-%d %H:%M:%S"
    )


def check_unique(name, values):

    duplicates = (
        len(values)
        - len(set(values))
    )

    if duplicates == 0:

        print(
            f"{name:<40} PASS"
        )

    else:

        print(
            f"{name:<40} FAIL "
            f"({duplicates} duplicates)"
        )

        issues.append(
            f"{name}: duplicate identifiers found"
        )


# ============================================================
# LOAD DATA
# ============================================================

orders = read_csv(
    "order_events.csv"
)

shipments = read_csv(
    "shipment_events.csv"
)

vehicles = read_csv(
    "vehicle_events.csv"
)

deliveries = read_csv(
    "delivery_events.csv"
)


datasets = {
    "order_events.csv": orders,
    "shipment_events.csv": shipments,
    "vehicle_events.csv": vehicles,
    "delivery_events.csv": deliveries
}


# ============================================================
# HEADER
# ============================================================

print("\n" + "=" * 75)
print("PHASE 3 BASELINE VALIDATION")
print("=" * 75)


# ============================================================
# 1. RECORD COUNT VALIDATION
# ============================================================

print("\n--- Record Count Validation ---")

for filename, rows in datasets.items():

    expected = EXPECTED_COUNTS[filename]

    actual = len(rows)

    if actual == expected:

        print(
            f"{filename:<30} "
            f"{actual:>6} / {expected:<6} PASS"
        )

    else:

        print(
            f"{filename:<30} "
            f"{actual:>6} / {expected:<6} FAIL"
        )

        issues.append(
            f"{filename}: expected {expected}, found {actual}"
        )


# ============================================================
# 2. COLUMN VALIDATION
# ============================================================

print("\n--- Column Structure Validation ---")

for filename, expected_columns in EXPECTED_COLUMNS.items():

    path = DATA_DIR / filename

    if not path.exists():
        continue

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        actual_columns = reader.fieldnames

    if actual_columns == expected_columns:

        print(
            f"{filename:<30} PASS"
        )

    else:

        print(
            f"{filename:<30} FAIL"
        )

        issues.append(
            f"{filename}: column structure mismatch"
        )


# ============================================================
# 3. IDENTIFIER VALIDATION
# ============================================================
#
# IMPORTANT:
#
# order_id is unique at the order level.
#
# shipment_id is NOT expected to be unique in
# shipment_events because one shipment generates
# multiple shipment events.
#
# vehicle_id is NOT expected to be unique in
# vehicle_events because one vehicle can generate
# multiple vehicle events.
#
# event_id MUST be unique because every event is
# an individual streaming record.
# ============================================================

print("\n--- Identifier Validation ---")


order_ids = [
    row["order_id"]
    for row in orders
]


shipment_ids = [
    row["shipment_id"]
    for row in shipments
]


shipment_event_ids = [
    row["event_id"]
    for row in shipments
]


vehicle_event_ids = [
    row["event_id"]
    for row in vehicles
]


delivery_event_ids = [
    row["event_id"]
    for row in deliveries
]


# Order IDs must be unique.

check_unique(
    "Order IDs",
    order_ids
)


# Event IDs must be unique.

check_unique(
    "Shipment Event IDs",
    shipment_event_ids
)

check_unique(
    "Vehicle Event IDs",
    vehicle_event_ids
)

check_unique(
    "Delivery Event IDs",
    delivery_event_ids
)


# Shipment IDs are allowed to repeat.
# Instead, verify that we have the expected
# number of distinct shipments.

unique_shipment_count = len(
    set(shipment_ids)
)

expected_unique_shipments = 1000


if unique_shipment_count == expected_unique_shipments:

    print(
        f"{'Unique Shipment IDs':<40} "
        f"{unique_shipment_count} / "
        f"{expected_unique_shipments} PASS"
    )

else:

    print(
        f"{'Unique Shipment IDs':<40} "
        f"{unique_shipment_count} / "
        f"{expected_unique_shipments} FAIL"
    )

    issues.append(
        "Unexpected number of unique shipment IDs"
    )


# ============================================================
# 4. REFERENTIAL INTEGRITY
# ============================================================

print("\n--- Referential Integrity ---")


order_id_set = set(
    order_ids
)

shipment_id_set = set(
    shipment_ids
)


invalid_shipment_orders = [

    row
    for row in shipments

    if row["order_id"]
    not in order_id_set
]


invalid_vehicle_shipments = [

    row
    for row in vehicles

    if row["shipment_id"]
    not in shipment_id_set
]


invalid_delivery_shipments = [

    row
    for row in deliveries

    if row["shipment_id"]
    not in shipment_id_set
]


if not invalid_shipment_orders:

    print(
        "Shipment → Order references          PASS"
    )

else:

    print(
        "Shipment → Order references          FAIL"
    )

    issues.append(
        "Invalid shipment → order references"
    )


if not invalid_vehicle_shipments:

    print(
        "Vehicle → Shipment references        PASS"
    )

else:

    print(
        "Vehicle → Shipment references        FAIL"
    )

    issues.append(
        "Invalid vehicle → shipment references"
    )


if not invalid_delivery_shipments:

    print(
        "Delivery → Shipment references       PASS"
    )

else:

    print(
        "Delivery → Shipment references       FAIL"
    )

    issues.append(
        "Invalid delivery → shipment references"
    )


# ============================================================
# 5. REQUIRED FIELD VALIDATION
# ============================================================

print("\n--- Required Field Validation ---")


for filename, rows in datasets.items():

    required_columns = EXPECTED_COLUMNS[
        filename
    ]

    missing_count = 0

    for row in rows:

        for column in required_columns:

            if (
                column not in row
                or row[column] is None
                or str(row[column]).strip() == ""
            ):

                missing_count += 1


    if missing_count == 0:

        print(
            f"{filename:<30} PASS"
        )

    else:

        print(
            f"{filename:<30} FAIL "
            f"({missing_count} missing values)"
        )

        issues.append(
            f"{filename}: missing required values"
        )


# ============================================================
# 6. TIMESTAMP VALIDATION
# ============================================================

print("\n--- Timestamp Validation ---")


timestamp_columns = {

    "order_events.csv": [
        "order_timestamp"
    ],

    "shipment_events.csv": [
        "event_timestamp"
    ],

    "vehicle_events.csv": [
        "event_timestamp"
    ],

    "delivery_events.csv": [
        "event_timestamp",
        "expected_delivery_timestamp",
        "actual_delivery_timestamp"
    ]
}


for filename, rows in datasets.items():

    invalid = 0

    for row in rows:

        for column in timestamp_columns[
            filename
        ]:

            try:

                parse_timestamp(
                    row[column]
                )

            except Exception:

                invalid += 1


    if invalid == 0:

        print(
            f"{filename:<30} PASS"
        )

    else:

        print(
            f"{filename:<30} FAIL "
            f"({invalid} invalid timestamps)"
        )

        issues.append(
            f"{filename}: invalid timestamps"
        )


# ============================================================
# 7. ORDER PRIORITY VALIDATION
# ============================================================

print("\n--- Order Priority Validation ---")


invalid_priorities = [

    row
    for row in orders

    if row["priority"]
    not in VALID_PRIORITIES
]


if not invalid_priorities:

    print(
        "Order priority values                PASS"
    )

else:

    print(
        "Order priority values                FAIL"
    )

    issues.append(
        "Invalid order priority values"
    )


# ============================================================
# 8. VEHICLE STATUS VALIDATION
# ============================================================

print("\n--- Vehicle Status Validation ---")


invalid_vehicle_statuses = [

    row
    for row in vehicles

    if row["vehicle_status"]
    not in VALID_VEHICLE_STATUSES
]


if not invalid_vehicle_statuses:

    print(
        "Vehicle status values                PASS"
    )

else:

    print(
        "Vehicle status values                FAIL"
    )

    issues.append(
        "Invalid vehicle status values"
    )


# ============================================================
# 9. DELIVERY STATUS VALIDATION
# ============================================================

print("\n--- Delivery Status Validation ---")


invalid_delivery_statuses = [

    row
    for row in deliveries

    if row["delivery_status"]
    not in VALID_DELIVERY_STATUSES
]


if not invalid_delivery_statuses:

    print(
        "Delivery status values               PASS"
    )

else:

    print(
        "Delivery status values               FAIL"
    )

    issues.append(
        "Invalid delivery status values"
    )


# ============================================================
# 10. ORDER VALUE VALIDATION
# ============================================================

print("\n--- Numeric Validation ---")


invalid_order_values = 0

for row in orders:

    try:

        value = float(
            row["order_value"]
        )

        if value <= 0:
            invalid_order_values += 1

    except Exception:

        invalid_order_values += 1


if invalid_order_values == 0:

    print(
        "Order value values                  PASS"
    )

else:

    print(
        f"Order value values                  FAIL "
        f"({invalid_order_values} errors)"
    )

    issues.append(
        "Invalid order value values"
    )


# ============================================================
# 11. VEHICLE SPEED VALIDATION
# ============================================================

invalid_speeds = 0

for row in vehicles:

    try:

        speed = float(
            row["speed_kmh"]
        )

        if speed < 0:

            invalid_speeds += 1

    except Exception:

        invalid_speeds += 1


if invalid_speeds == 0:

    print(
        "Vehicle speed values                PASS"
    )

else:

    print(
        f"Vehicle speed values                FAIL "
        f"({invalid_speeds} errors)"
    )

    issues.append(
        "Invalid vehicle speed values"
    )


# ============================================================
# 12. DELIVERY DELAY VALIDATION
# ============================================================

print("\n--- Delivery Delay Validation ---")


delay_errors = 0


for row in deliveries:

    try:

        expected = parse_timestamp(
            row[
                "expected_delivery_timestamp"
            ]
        )

        actual = parse_timestamp(
            row[
                "actual_delivery_timestamp"
            ]
        )

        calculated_delay = int(
            (
                actual - expected
            ).total_seconds()
            / 60
        )

        recorded_delay = int(
            row["delay_minutes"]
        )

        if calculated_delay != recorded_delay:

            delay_errors += 1

    except Exception:

        delay_errors += 1


if delay_errors == 0:

    print(
        "Delivery delay calculations         PASS"
    )

else:

    print(
        f"Delivery delay calculations         FAIL "
        f"({delay_errors} errors)"
    )

    issues.append(
        "Delivery delay calculations inconsistent"
    )


# ============================================================
# 13. DELIVERY STATUS / EVENT TYPE CONSISTENCY
# ============================================================

print("\n--- Delivery Event Consistency ---")


delivery_event_errors = 0


for row in deliveries:

    status = row[
        "delivery_status"
    ]

    event_type = row[
        "event_type"
    ]


    if (
        status == "DELIVERED"
        and event_type != "DELIVERY_COMPLETED"
    ):

        delivery_event_errors += 1


    if (
        status == "FAILED"
        and event_type != "DELIVERY_FAILED"
    ):

        delivery_event_errors += 1


if delivery_event_errors == 0:

    print(
        "Delivery status/event consistency    PASS"
    )

else:

    print(
        f"Delivery status/event consistency    FAIL "
        f"({delivery_event_errors} errors)"
    )

    issues.append(
        "Delivery status/event type mismatch"
    )


# ============================================================
# 14. TOTAL EVENT COUNT
# ============================================================

print("\n--- Overall Event Volume ---")


total_events = (
    len(orders)
    + len(shipments)
    + len(vehicles)
    + len(deliveries)
)


print(
    f"Total events: {total_events:,}"
)


if total_events == EXPECTED_TOTAL_EVENTS:

    print(
        "Total event count                   PASS"
    )

else:

    print(
        "Total event count                   FAIL"
    )

    issues.append(
        f"Expected {EXPECTED_TOTAL_EVENTS} "
        f"events, found {total_events}"
    )


# ============================================================
# 15. FINAL VALIDATION RESULT
# ============================================================

print("\n" + "=" * 75)


if not issues:

    print(
        "VALIDATION RESULT: PASS"
    )

    print(
        "Phase 3 baseline is ready for Kafka streaming."
    )

else:

    print(
        "VALIDATION RESULT: FAIL"
    )

    print(
        f"Issues detected: {len(issues)}"
    )

    print("\nIssues:")

    for issue in issues:

        print(
            f"- {issue}"
        )


print("=" * 75)