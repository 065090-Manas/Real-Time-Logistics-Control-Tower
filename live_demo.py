import json
import time
import random
from datetime import datetime, timedelta

from kafka import KafkaProducer


# ============================================================
# REAL-TIME LOGISTICS CONTROL TOWER
# LIVE STREAMING DEMONSTRATION
# Kafka -> Python Consumer -> MySQL -> Grafana
# ============================================================

KAFKA_SERVER = "localhost:9092"

# Run time: approximately 3 minutes
DEMO_DURATION_SECONDS = 180

# Send new events every 5 seconds
EVENT_INTERVAL_SECONDS = 5


# Existing shipments from the analytical dataset
SHIPMENTS = [
    {
        "shipment_id": "SHP00090",
        "order_id": "ORD00090",
        "zone": "Ghaziabad",
        "vehicle_id": "VEH00090"
    },
    {
        "shipment_id": "SHP00518",
        "order_id": "ORD00518",
        "zone": "Gurgaon",
        "vehicle_id": "VEH00518"
    },
    {
        "shipment_id": "SHP00846",
        "order_id": "ORD00846",
        "zone": "Delhi",
        "vehicle_id": "VEH00846"
    },
    {
        "shipment_id": "SHP00860",
        "order_id": "ORD00860",
        "zone": "Gurgaon",
        "vehicle_id": "VEH00860"
    },
    {
        "shipment_id": "SHP00648",
        "order_id": "ORD00648",
        "zone": "Faridabad",
        "vehicle_id": "VEH00648"
    },
    {
        "shipment_id": "SHP00886",
        "order_id": "ORD00886",
        "zone": "Faridabad",
        "vehicle_id": "VEH00886"
    },
    {
        "shipment_id": "SHP00414",
        "order_id": "ORD00414",
        "zone": "Gurgaon",
        "vehicle_id": "VEH00414"
    },
    {
        "shipment_id": "SHP00451",
        "order_id": "ORD00451",
        "zone": "Jaipur",
        "vehicle_id": "VEH00451"
    },
]


# ------------------------------------------------------------
# Kafka Producer
# ------------------------------------------------------------

print("=" * 70)
print("REAL-TIME LOGISTICS CONTROL TOWER")
print("3-MINUTE LIVE STREAMING DEMONSTRATION")
print("Kafka -> Python -> MySQL -> Grafana")
print("=" * 70)

print("\nConnecting to Kafka...")

producer = KafkaProducer(
    bootstrap_servers=KAFKA_SERVER,
    value_serializer=lambda value: json.dumps(value).encode("utf-8")
)

print("Connected to Kafka")

print("\nLive topics:")
print("  - vehicle_events")
print("  - delivery_events")

print("\nStarting live stream...")
print("Events will be sent every 5 seconds.")
print("Press CTRL+C to stop early.\n")

print("-" * 70)


# ------------------------------------------------------------
# Generate changing delay values
# ------------------------------------------------------------

delay_patterns = [
    15,
    22,
    31,
    45,
    58,
    72,
    85,
    105,
    125,
    145,
    90,
    65,
    48,
    35,
    20
]


start_time = time.time()
cycle = 0
event_counter = 0


try:

    while time.time() - start_time < DEMO_DURATION_SECONDS:

        cycle += 1

        # Select shipment in rotating order
        shipment = SHIPMENTS[(cycle - 1) % len(SHIPMENTS)]

        shipment_id = shipment["shipment_id"]
        order_id = shipment["order_id"]
        zone = shipment["zone"]
        vehicle_id = shipment["vehicle_id"]

        # Changing delay pattern
        base_delay = delay_patterns[(cycle - 1) % len(delay_patterns)]

        # Small random variation
        delay = max(
            0,
            base_delay + random.randint(-5, 8)
        )

        # Vehicle states change during the demonstration
        vehicle_states = [
            "MOVING",
            "MOVING",
            "DELAYED",
            "STOPPED",
            "MOVING",
            "IDLE"
        ]

        vehicle_status = vehicle_states[(cycle - 1) % len(vehicle_states)]

        # Speed based on vehicle status
        if vehicle_status == "MOVING":
            speed = random.randint(35, 65)

        elif vehicle_status == "DELAYED":
            speed = random.randint(5, 20)

        elif vehicle_status == "STOPPED":
            speed = 0

        else:
            speed = 0

        now = datetime.now()

        expected_time = now + timedelta(minutes=30)

        actual_time = expected_time + timedelta(minutes=delay)

        # ----------------------------------------------------
        # VEHICLE EVENT
        # ----------------------------------------------------

        vehicle_event = {
            "event_id": f"LIVE_VEH_{cycle:04d}",
            "event_timestamp": now.isoformat(),
            "event_type": "VEHICLE_STATUS_UPDATE",
            "vehicle_id": vehicle_id,
            "shipment_id": shipment_id,
            "zone": zone,
            "vehicle_status": vehicle_status,
            "speed_kmh": speed
        }

        producer.send(
            "vehicle_events",
            vehicle_event
        )

        producer.flush()

        event_counter += 1

        print("\n[KAFKA] Vehicle Event")
        print(
            f"Shipment={shipment_id} | "
            f"Status={vehicle_status} | "
            f"Speed={speed} km/h | "
            f"Zone={zone}"
        )


        # ----------------------------------------------------
        # DELIVERY EVENT
        # ----------------------------------------------------

        delivery_event = {
            "event_id": f"LIVE_DEL_{cycle:04d}",
            "event_timestamp": now.isoformat(),
            "event_type": "DELIVERY_DELAY",
            "shipment_id": shipment_id,
            "order_id": order_id,
            "destination_zone": zone,
            "expected_delivery_timestamp": expected_time.isoformat(),
            "actual_delivery_timestamp": actual_time.isoformat(),
            "delay_minutes": delay,
            "delivery_status": "DELIVERED"
        }

        producer.send(
            "delivery_events",
            delivery_event
        )

        producer.flush()

        event_counter += 1

        print(
            f"[KAFKA] Delivery Event | "
            f"Shipment={shipment_id} | "
            f"Delay={delay} min"
        )

        print(
            f"[LIVE STREAM] Event #{event_counter} | "
            f"Cycle={cycle} | "
            f"Elapsed={int(time.time() - start_time)} sec"
        )

        print("-" * 70)

        # Wait before next event cycle
        time.sleep(EVENT_INTERVAL_SECONDS)


except KeyboardInterrupt:

    print("\n\nLive demo stopped manually.")


finally:

    producer.flush()
    producer.close()

    elapsed = int(time.time() - start_time)

    print("\n" + "=" * 70)
    print("LIVE STREAMING DEMONSTRATION COMPLETED")
    print(f"Duration: {elapsed} seconds")
    print(f"Events sent: {event_counter}")
    print("=" * 70)