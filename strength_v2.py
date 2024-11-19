import sys
from datetime import datetime
from garminconnect import Garmin
import json
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get credentials from environment variables
username = os.getenv("GARMIN_USERNAME")
password = os.getenv("GARMIN_PASSWORD")

# Check if username and password are defined
if not username or not password:
    print("Error: Missing GARMIN_USERNAME or GARMIN_PASSWORD in .env file.")
    sys.exit(1)

# Function to log in to Garmin Connect
def login_to_garmin():
    try:
        client = Garmin(username, password)
        client.login()
        print("Logged in successfully!")
        return client
    except Exception as e:
        print(f"Login failed: {e}")
        sys.exit(1)

# Check if the correct number of arguments are passed
if len(sys.argv) != 2:
    print("Usage: python script.py YYYY-MM-DD")
    sys.exit(1)

# Parse the start date argument
start_date_str = sys.argv[1]
try:
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
except ValueError:
    print("Invalid date format. Please use YYYY-MM-DD.")
    sys.exit(1)

# Log in to Garmin Connect
client = login_to_garmin()

# Fetch activities and filter by start date and type
try:
    activities = client.get_activities(0, 100)  # Fetch the latest 100 activities
except Exception as e:
    print(f"Failed to fetch activities: {e}")
    sys.exit(1)

# Filter and collect strength training activities after the start date
strength_training = []
for act in activities:
    try:
        activity_date = datetime.strptime(act['startTimeLocal'], "%Y-%m-%d %H:%M:%S")
        if act['activityType']['typeKey'] == 'strength_training' and activity_date >= start_date:
            # Append only if 'movingDuration' exists
            if 'movingDuration' in act:
                strength_training.append(act)
    except KeyError as e:
        print(f"Missing expected key in activity: {e}")
    except ValueError:
        print(f"Skipping activity with invalid date format: {act['startTimeLocal']}")

# Aggregate total time
total_time = sum(act.get('movingDuration', 0) for act in strength_training) / 60  # in minutes
print(f"Total strength training time since {start_date_str}: {total_time:.2f} minutes")
