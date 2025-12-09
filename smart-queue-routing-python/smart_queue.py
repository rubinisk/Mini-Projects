import csv
import numpy as np

def read_sensor_live(filename="sensor.csv"):
    """Read sensor data (time, c1, c2, c3, c4) from CSV."""
    data = []
    try:
        with open(filename, "r", newline="") as f:
            r = csv.reader(f)
            header = next(r, None)
            if header is None:
                print("sensor.csv is empty!")
                return []

            for row in r:
                if len(row) < 5:
                    continue
                ts = float(row[0])
                c1 = int(row[1])
                c2 = int(row[2])
                c3 = int(row[3])
                c4 = int(row[4])
                data.append((ts, c1, c2, c3, c4))

        print("Raw sensor data loaded (first 10 rows):", data[:10])
        return data
    except FileNotFoundError:
        print("sensor.csv not found!")
        return []

def create_customers_from_sensor(sensor_data):
    """Convert cumulative sensor counts into individual customers."""
    customers = []
    previous = np.zeros(4, dtype=int)
    customer_id = 1

    print("\n=== CUSTOMER CREATION FROM SENSOR ===")
    for ts, c1, c2, c3, c4 in sensor_data:
        current = np.array([c1, c2, c3, c4], dtype=int)
        increments = current - previous

        print(f"Time: {ts} | Counts: {current} | New People: {increments}")
        for counter_index in range(4):
            if increments[counter_index] > 0:
                for _ in range(increments[counter_index]):
                    customers.append({"id": customer_id, "arrival": ts})
                    print(f"Created Customer {customer_id} at time {ts}")
                    customer_id += 1

        previous = current

    print("Total customers created:", len(customers))
    return customers

def simulate_multi_counter(customers):
    """Simulate routing of customers across 4 counters with capacity limits."""
    counter_count = 4
    service_times = [3.5, 5.0, 4.0, 3.0]
    max_capacity = 5

    print(f"\nMax persons per counter = {max_capacity}")

    counters = [
        {"free_at": 0.0, "queue": [], "service": service_times[i]}
        for i in range(counter_count)
    ]

    results = []
    suggestions = []
    screen_messages = []

    print("\n=== SIMULATION STARTED ===")
    for c in customers:
        arrival = c["arrival"]

        predicted_waits = [
            len(counter["queue"]) * counter["service"] for counter in counters
        ]
        chosen_index = predicted_waits.index(min(predicted_waits))

        if len(counters[chosen_index]["queue"]) >= max_capacity:
            print(f"Counter {chosen_index+1} FULL → redirecting Customer {c['id']}")
            available = [
                i for i in range(counter_count)
                if len(counters[i]["queue"]) < max_capacity
            ]
            if available:
                chosen_index = min(
                    available, key=lambda x: len(counters[x]["queue"])
                )
                suggestions.append(
                    f"Customer {c['id']} redirected → Counter {chosen_index+1}"
                )
                screen_messages.append(
                    f"Counter {chosen_index+1} has space, please move."
                )
            else:
                warning = f"ALL counters FULL! Customer {c['id']} must wait."
                suggestions.append(warning)
                screen_messages.append(warning)

        counter = counters[chosen_index]
        wait = max(0.0, counter["free_at"] - arrival)
        start = arrival + wait
        end = start + counter["service"]

        print(f"Customer {c['id']} → Counter {chosen_index+1} | Wait: {wait:.2f}")

        counter["free_at"] = end
        counter["queue"].append(c["id"])

        results.append({
            "id": c["id"],
            "arrival": arrival,
            "start": start,
            "end": end,
            "wait": wait,
            "counter": chosen_index + 1,
            "queue_after_join": len(counter["queue"]),
            "predicted_wait": predicted_waits[chosen_index],
        })

    print("=== SIMULATION FINISHED ===")
    return results, suggestions, screen_messages

def save_outputs(results, suggestions, screen_msgs):
    """Save results and messages to CSV/TXT files."""
    with open("queue_smart.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "ID", "Arrival", "Start", "End", "Wait",
            "Counter", "QueueAfterJoin", "PredictedWait",
        ])
        for r in results:
            w.writerow([
                r["id"], r["arrival"], r["start"], r["end"],
                r["wait"], r["counter"], r["queue_after_join"],
                r["predicted_wait"],
            ])

    with open("suggestions.txt", "w", encoding="utf-8") as f:
        for s in suggestions:
            f.write(s + "\n")

    with open("screen_messages.txt", "w", encoding="utf-8") as f:
        for s in screen_msgs:
            f.write(s + "\n")

    print("Saved queue_smart.csv, suggestions.txt, screen_messages.txt")

def main():
    print("=== SMART 4-COUNTER QUEUE SYSTEM ===")

    sensor_data = read_sensor_live()
    print("Loaded rows:", len(sensor_data))
    print("First 5 rows:", sensor_data[:5])

    if not sensor_data:
        return

    customers = create_customers_from_sensor(sensor_data)
    results, suggestions, screen_msgs = simulate_multi_counter(customers)

    print("\n=== FIRST 3 RESULTS ===")
    for r in results[:3]:
        print(r)

    wait_times = np.array([r["wait"] for r in results])
    print("\n=== WAITING TIME STATISTICS ===")
    print("Average wait:", float(np.mean(wait_times)))
    print("Max wait:", float(np.max(wait_times)))
    print("Min wait:", float(np.min(wait_times)))

    save_outputs(results, suggestions, screen_msgs)

    print("\n=== SMART SUGGESTIONS ===")
    for s in suggestions:
        print(s)

    print("\n=== DISPLAY SCREEN MESSAGES ===")
    for s in screen_msgs:
        print(s)

if __name__ == "__main__":
    main()