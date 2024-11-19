import sys
from datetime import datetime
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

# Check if the correct number of arguments are passed
if len(sys.argv) != 2:
    print("Usage: python script.py YYYY-MM-DD")
    sys.exit(1)

# Parse the date argument
start_date_str = sys.argv[1]
try:
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
except ValueError:
    print("Invalid date format. Please use YYYY-MM-DD.")
    sys.exit(1)

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

# Initialize the total moving duration and push-up / pull-up counters
total_moving_duration = 0
total_pushups = 0
total_pullups = 0

# Process each activity and aggregate movingDuration for strength training activities
for act in activities:
    try:
        activity_date = datetime.strptime(act['startTimeLocal'], "%Y-%m-%d %H:%M:%S")
        
        # Filter activities based on type and start date
        if act['activityType']['typeKey'] == 'strength_training' and activity_date >= start_date:
            # Aggregate moving duration (in seconds)
            total_moving_duration += act.get('movingDuration', 0)

            # Count reps for PUSH_UP and PULL_UP in summarizedExerciseSets
            if 'summarizedExerciseSets' in act:
                for exercise in act['summarizedExerciseSets']:
                    if exercise['category'] == 'PUSH_UP':
                        total_pushups += exercise['reps']
                    elif exercise['category'] == 'PULL_UP':
                        total_pullups += exercise['reps']

    except KeyError as e:
        print(f"Missing expected key in activity: {e}")
    except ValueError:
        print(f"Skipping activity with invalid date format: {act['startTimeLocal']}")

# Output the results
print(f"Total moving duration for strength training activities since {start_date_str}: {total_moving_duration / 60:.2f} minutes")
print(f"Total PUSH_UP reps since {start_date_str}: {total_pushups}")
print(f"Total PULL_UP reps since {start_date_str}: {total_pullups}")

