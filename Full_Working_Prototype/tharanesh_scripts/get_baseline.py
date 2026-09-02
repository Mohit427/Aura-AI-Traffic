import psycopg2
import json

DB_CONFIG = {
    "dbname": "aura_db",
    "user": "aura_user",
    "password": "aura_pass_hackathon",
    "host": "localhost",
    "port": "5432"
}

def get_real_world_averages():
    print("Connecting to backend database to calculate real-world baseline...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        cur.execute("SELECT counts FROM vision_logs ORDER BY timestamp DESC LIMIT 100;")
        rows = cur.fetchall()

        total_cars = 0
        valid_logs = 0

        for row in rows:
            counts = row[0]
            if isinstance(counts, dict) and "car" in counts:
                total_cars += counts["car"]
                valid_logs += 1

        if valid_logs > 0:
            avg_cars = total_cars / valid_logs
            print(f"✅ Success! The real-world average is {round(avg_cars, 2)} cars per detection cycle.")
        else:
            print("No valid car counts found in the database.")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"Database error: {e}")
        print("Double-check that Mohit's PostgreSQL server is running!")

if __name__ == "__main__":
    get_real_world_averages()
