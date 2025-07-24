import csv
import os
import random
from datetime import datetime, timedelta

# ---------- CONFIG ----------
user_id = 100  # Number of apps to generate
actions = ["login", "logout", "ad_click", "view_product", "add_to_cart", "remove_from_cart","purchase","search"]


start_date = datetime(2018, 1, 1)
end_date = datetime(2025, 7, 16)

file_location = "E:\Apple\data"
os.makedirs(file_location, exist_ok=True)
csv_file_path = os.path.join(file_location, "apps.csv")

# ---------- GENERATION ----------
with open(csv_file_path, "w", newline="", encoding="utf-8") as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(["user_id", "action"])

    for user_id in range(1, user_id + 1):
        user_id = f"{user_id}"
        action = random.choice(actions)

        csvwriter.writerow([user_id, action])

print("✅ apps.csv generated successfully!")
