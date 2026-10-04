import subprocess
import sys
import threading
from pathlib import Path


# ============================================================
# REAL-TIME LOGISTICS CONTROL TOWER
# PHASE 5.11 — INTEGRATED PRODUCER LAUNCHER
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

PRODUCER_DIR = BASE_DIR / "producers"


# ============================================================
# PRODUCERS
# ============================================================

PRODUCERS = [

    ("ORDER", PRODUCER_DIR / "order_producer.py"),

    ("SHIPMENT", PRODUCER_DIR / "shipment_producer.py"),

    ("VEHICLE", PRODUCER_DIR / "vehicle_producer.py"),

    ("DELIVERY", PRODUCER_DIR / "delivery_producer.py"),

]


# ============================================================
# HEADER
# ============================================================

print("=" * 80)
print("REAL-TIME LOGISTICS CONTROL TOWER")
print("PHASE 5.11 — INTEGRATED STREAMING")
print("=" * 80)

print()
print("Starting all four Kafka producers simultaneously...")
print()

print("Streams:")
print("  1. ORDER    → order_events")
print("  2. SHIPMENT → shipment_events")
print("  3. VEHICLE  → vehicle_events")
print("  4. DELIVERY → delivery_events")

print()
print("=" * 80)


# ============================================================
# CHECK PRODUCER FILES
# ============================================================

missing_files = []

for name, producer_file in PRODUCERS:

    if not producer_file.exists():

        missing_files.append(
            f"{name}: {producer_file}"
        )


if missing_files:

    print()
    print("ERROR: The following producer files are missing:")

    for file in missing_files:
        print(f"  - {file}")

    print()
    sys.exit(1)


# ============================================================
# RUN PRODUCER
# ============================================================

def run_producer(name, producer_file):

    print(
        f"[STARTED] {name} producer"
    )

    try:

        process = subprocess.Popen(

            [
                sys.executable,
                str(producer_file)
            ],

            stdout=subprocess.PIPE,

            stderr=subprocess.STDOUT,

            text=True,

            encoding="utf-8",

            errors="replace",

            bufsize=1
        )


        # ----------------------------------------------------
        # DISPLAY OUTPUT WITH STREAM NAME
        # ----------------------------------------------------

        for line in process.stdout:

            line = line.rstrip()

            if line:

                print(
                    f"[{name}] {line}",
                    flush=True
                )


        return_code = process.wait()


        # ----------------------------------------------------
        # FINAL STATUS
        # ----------------------------------------------------

        if return_code == 0:

            print(
                f"[COMPLETED] {name} producer"
            )

        else:

            print(
                f"[FAILED] {name} producer "
                f"(Exit code: {return_code})"
            )


    except Exception as error:

        print(
            f"[ERROR] {name} producer: {error}"
        )


# ============================================================
# START ALL PRODUCERS
# ============================================================

threads = []


for name, producer_file in PRODUCERS:

    thread = threading.Thread(

        target=run_producer,

        args=(name, producer_file),

        daemon=False
    )

    threads.append(thread)

    thread.start()


# ============================================================
# WAIT FOR ALL PRODUCERS
# ============================================================

for thread in threads:

    thread.join()


# ============================================================
# FINAL MESSAGE
# ============================================================

print()
print("=" * 80)
print("INTEGRATED STREAMING RUN COMPLETE")
print("=" * 80)

print()
print("All producer processes have finished.")
print()
print("Streams tested:")
print("  ✓ order_events")
print("  ✓ shipment_events")
print("  ✓ vehicle_events")
print("  ✓ delivery_events")

print()
print("Next step: Validate the integrated Kafka message flow.")
print("=" * 80)