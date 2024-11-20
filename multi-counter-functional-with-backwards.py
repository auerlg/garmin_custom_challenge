import json
from datetime import datetime
from garminconnect import Garmin
from dotenv import load_dotenv
import os


def load_user_credentials(input_file):
    """
    Load login credentials from the JSON input file.
    Args:
        input_file (str): Path to the JSON file containing user credentials.
    Returns:
        list: A list of user dictionaries containing 'prettyname', 'login_email', 'login_password'.
    """
    try:
        with open(input_file, 'r') as file:
            users = json.load(file)
        return users
    except Exception as e:
        print(f"Error reading input file: {e}")
        return []


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


def aggregate_activities_by_criteria(activities, start_date, input_file):
    """
    Aggregate values for activities based on activity type, tag, and aggregation parameter 
    from the JSON input file. Scaling (multiplicator) is applied only at the end.
    Args:
        activities (list): List of activity dictionaries fetched from Garmin Connect.
        start_date (datetime): The starting date to filter activities.
        input_file (str): Path to the JSON file containing aggregation criteria.
    Returns:
        dict: A dictionary with descriptions of criteria and their raw aggregated values.
        dict: A dictionary mapping each criterion to its unit and multiplicator for output.
    """
    try:
        with open(input_file, 'r') as file:
            criteria_list = json.load(file)
    except Exception as e:
        print(f"Error reading input file: {e}")
        return {}, {}

    raw_results = {}
    metadata = {}

    for criterion in criteria_list:
        activity_type = criterion.get("activityType", "")
        tag = criterion.get("tag", "").lower()
        parameter = criterion.get("aggregationParameter", "")
        multiplicator = criterion.get("multiplicator", 1)
        unit = criterion.get("unit", "")
        description = f"{activity_type or 'any'}-{tag or 'any'}-{parameter}"

        raw_results[description] = 0.0
        metadata[description] = {"multiplicator": multiplicator, "unit": unit}

        for act in activities:
            try:
                activity_date = datetime.strptime(act['startTimeLocal'], "%Y-%m-%d %H:%M:%S")
                if activity_date >= start_date:
                    matches_type = not activity_type or act['activityType']['typeKey'] == activity_type
                    matches_tag = not tag or ('description' in act and tag in act['description'].lower())

                    if matches_type and matches_tag:
                        value = act.get(parameter, 0.0)
                        raw_results[description] += value
            except (KeyError, ValueError):
                continue

    return raw_results, metadata


def main():
    # Load users' credentials from the JSON input file
    input_file = "users.json"  # Path to the JSON file
    users = load_user_credentials(input_file)

    # Specify the start date for the aggregation
    start_date_str = "2024-11-01"
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")

    # Process each user in the JSON file
    for user in users:
        prettyname = user['prettyname']
        login_email = user['login_email']
        login_password = user['login_password']
        
        # Login to Garmin Connect for each user
        try:
            client = Garmin(login_email, login_password)
            client.login()
            print(f"Logged in successfully as {prettyname}!")
        except Exception as e:
            print(f"Login failed for {prettyname}: {e}")
            continue
        
        # Fetch activities for the logged-in user
        activities = client.get_activities(0, 100)  # Fetch the latest 100 activities
        print(f"Fetched activities successfully for {prettyname}!")

        # Count push-ups and pull-ups for the user
        pushups, pullups = count_pushups_pullups(activities, start_date)
        print(f"Total PUSH_UP reps for {prettyname}: {pushups}")
        print(f"Total PULL_UP reps for {prettyname}: {pullups}")

        # Aggregate the activities based on the criteria
        results, metadata = aggregate_activities_by_criteria(activities, start_date, "list-tags.json")

        # Print the results for each user
        print(f"Results for {prettyname}:")
        for description, raw_total in results.items():
            multiplicator = metadata[description]["multiplicator"]
            unit = metadata[description]["unit"]
            scaled_total = raw_total * multiplicator  # Apply multiplicator after aggregation
            print(f"Total {description}: {scaled_total:.2f} {unit}")
        print("-" * 40)


if __name__ == "__main__":
    main()
