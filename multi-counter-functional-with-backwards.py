import sys
from datetime import datetime
from garminconnect import Garmin
from dotenv import load_dotenv
import os


def load_credentials():
    """Load credentials from environment variables."""
    load_dotenv()
    username = os.getenv("GARMIN_USERNAME")
    password = os.getenv("GARMIN_PASSWORD")

    if not username or not password:
        print("Error: Missing GARMIN_USERNAME or GARMIN_PASSWORD in .env file.")
        sys.exit(1)

    return username, password


def parse_start_date():
    """Parse the start date argument from command line."""
    if len(sys.argv) != 2:
        print("Usage: python script.py YYYY-MM-DD")
        sys.exit(1)

    start_date_str = sys.argv[1]
    try:
        return datetime.strptime(start_date_str, "%Y-%m-%d")
    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD.")
        sys.exit(1)


def login_to_garmin(username, password):
    """Log in to Garmin Connect."""
    try:
        client = Garmin(username, password)
        client.login()
        print("Logged in successfully!")
        return client
    except Exception as e:
        print(f"Login failed: {e}")
        sys.exit(1)


def fetch_activities(client):
    """Fetch the latest activities from Garmin Connect."""
    try:
        activities = client.get_activities(0, 100)  # Fetch the latest 100 activities
        print("Fetched activities successfully!")
        return activities
    except Exception as e:
        print(f"Failed to fetch activities: {e}")
        sys.exit(1)


def calculate_moving_duration(activities, start_date):
    """Calculate total moving duration for strength training activities."""
    total_duration = 0
    for act in activities:
        try:
            activity_date = datetime.strptime(act['startTimeLocal'], "%Y-%m-%d %H:%M:%S")
            if act['activityType']['typeKey'] == 'strength_training' and activity_date >= start_date:
                total_duration += act.get('movingDuration', 0)
        except (KeyError, ValueError):
            continue
    return total_duration


def count_pushups_pullups(activities, start_date):
    """Count total push-ups and pull-ups from strength training activities."""
    pushups = 0
    pullups = 0
    for act in activities:
        try:
            activity_date = datetime.strptime(act['startTimeLocal'], "%Y-%m-%d %H:%M:%S")
            if act['activityType']['typeKey'] == 'strength_training' and activity_date >= start_date:
                for exercise in act.get('summarizedExerciseSets', []):
                    if exercise['category'] == 'PUSH_UP':
                        pushups += exercise.get('reps', 0)
                    elif exercise['category'] == 'PULL_UP':
                        pullups += exercise.get('reps', 0)
        except (KeyError, ValueError):
            continue
    return pushups, pullups

def aggregate_backwards_distance(activities, start_date):
    """
    Calculate the total distance of activities containing 'backwards' in their description.

    Args:
        activities (list): List of activity dictionaries fetched from Garmin Connect.
        start_date (datetime): The starting date to filter activities.

    Returns:
        float: The total distance (in meters) of activities with 'backwards' in their description.
    """
    total_distance = 0.0
    for act in activities:
        try:
            activity_date = datetime.strptime(act['startTimeLocal'], "%Y-%m-%d %H:%M:%S")
            if activity_date >= start_date and 'description' in act:
                if 'backwards' in act['description'].lower():
                    total_distance += act.get('distance', 0.0)
        except (KeyError, ValueError):
            continue
    return total_distance


def main():
    username, password = load_credentials()
    start_date = parse_start_date()
    client = login_to_garmin(username, password)
    activities = fetch_activities(client)

    total_moving_duration = calculate_moving_duration(activities, start_date)
    pushups, pullups = count_pushups_pullups(activities, start_date)
# Aggregate the total distance for 'backwards' activities
    total_backwards_distance = aggregate_backwards_distance(activities, start_date)




    print(f"Total moving duration for strength training activities since {start_date}: {total_moving_duration / 60:.2f} minutes")
    print(f"Total PUSH_UP reps since {start_date}: {pushups}")
    print(f"Total PULL_UP reps since {start_date}: {pullups}")
    print(f"Total distance for activities with 'backwards' in the description since {start_date}: {total_backwards_distance / 1000:.2f} kilometers")



if __name__ == "__main__":
    main()
