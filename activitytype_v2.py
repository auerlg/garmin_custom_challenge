import json
from garminconnect import Garmin
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get credentials from environment variables
username = os.getenv("GARMIN_USERNAME")
password = os.getenv("GARMIN_PASSWORD")

# Check if username and password are provided
if not username or not password:
    print("Error: Missing GARMIN_USERNAME or GARMIN_PASSWORD in .env file.")
    exit(1)

# Login to Garmin Connect
try:
    client = Garmin(username, password)
    client.login()
    print("Logged in successfully!")
except Exception as e:
    print(f"Login failed: {e}")
    exit(1)

# Fetch activities
try:
    activities = client.get_activities(0, 100)  # Fetch the latest 100 activities
    print("Fetched activities successfully!")
except Exception as e:
    print(f"Failed to fetch activities: {e}")
    exit(1)

# List all activity types
print("Activity Types:")
for act in activities:
    if "activityType" in act and "typeKey" in act["activityType"]:
        print(act["activityType"]["typeKey"])
    else:
        print("Unknown activity type")

