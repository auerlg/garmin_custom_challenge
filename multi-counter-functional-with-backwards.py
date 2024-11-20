import sys
from datetime import datetime
from garminconnect import Garmin
from dotenv import load_dotenv
import os
import json



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

# def aggregate_activities_by_tags(activities, start_date, input_file):
#     """
#     Aggregate values for activities based on tags and parameters provided in a JSON input file.

#     Args:
#         activities (list): List of activity dictionaries fetched from Garmin Connect.
#         start_date (datetime): The starting date to filter activities.
#         input_file (str): Path to the JSON file containing tag-parameter pairs.

#     Returns:
#         dict: A dictionary with tags as keys and their aggregated values as values.
#     """
#     # Load tags and aggregation parameters from the JSON input file
#     try:
#         with open(input_file, 'r') as file:
#             tag_parameters = json.load(file)
#     except Exception as e:
#         print(f"Error reading input file: {e}")
#         return {}

#     # Initialize results dictionary
#     results = {tag: 0.0 for tag in tag_parameters}

#     # Process activities and aggregate values
#     for tag, parameter in tag_parameters.items():
#         for act in activities:
#             try:
#                 activity_date = datetime.strptime(act['startTimeLocal'], "%Y-%m-%d %H:%M:%S")
#                 if activity_date >= start_date:
#                     # Debugging: Check if the tag matches and the parameter exists
#                     if 'description' in act and tag in act['description'].lower():
#                         print(f"Matching tag '{tag}' in activity: {act['description']}")
#                         value = act.get(parameter, 0.0)
#                         print(f"Adding {value} for parameter '{parameter}'")
#                         results[tag] += value
#             except (KeyError, ValueError) as e:
#                 print(f"Skipped activity due to error: {e}")
#                 continue


#     return results

def aggregate_activities_by_criteria(activities, start_date, input_file):
    """
    Aggregate values for activities based on activity type, tag, and aggregation parameter from the JSON input file.

    Args:
        activities (list): List of activity dictionaries fetched from Garmin Connect.
        start_date (datetime): The starting date to filter activities.
        input_file (str): Path to the JSON file containing aggregation criteria.

    Returns:
        dict: A dictionary with descriptions of criteria and their aggregated values.
    """
    try:
        # Load criteria from the JSON input file
        with open(input_file, 'r') as file:
            criteria_list = json.load(file)
    except Exception as e:
        print(f"Error reading input file: {e}")
        return {}

    # Initialize results dictionary
    results = {}

    # Process each criterion
    for criterion in criteria_list:
        activity_type = criterion.get("activityType", "")
        tag = criterion.get("tag", "").lower()
        parameter = criterion.get("aggregationParameter", "")
        description = f"{activity_type or 'any'}-{tag or 'any'}-{parameter}"

        # Initialize the result for this criterion
        results[description] = 0.0

        # Aggregate values for the current criterion
        for act in activities:
            try:
                activity_date = datetime.strptime(act['startTimeLocal'], "%Y-%m-%d %H:%M:%S")
                if activity_date >= start_date:
                    # Match based on activityType or tag (if provided)
                    matches_type = not activity_type or act['activityType']['typeKey'] == activity_type
                    matches_tag = not tag or ('description' in act and tag in act['description'].lower())

                    if matches_type and matches_tag:
                        value = act.get(parameter, 0.0)
                        results[description] += value
            except (KeyError, ValueError):
                continue

    return results



def main():
    username, password = load_credentials()
    start_date = parse_start_date()
    client = login_to_garmin(username, password)
    activities = fetch_activities(client)

    total_moving_duration = calculate_moving_duration(activities, start_date)
    pushups, pullups = count_pushups_pullups(activities, start_date)
    # input_file = "list-tags.json"  # Path to the JSON file
    # # Load the JSON file to access the parameter for each tag
    # with open("list-tags.json", "r") as file:
    #     tag_parameters = json.load(file)
    # results = aggregate_activities_by_tags(activities, start_date, input_file)




    # Aggregate based on criteria in the input file
    input_file = "list-tags.json"  # Path to the JSON file
    results = aggregate_activities_by_criteria(activities, start_date, input_file)





    print(f"Total moving duration for strength training activities since {start_date}: {total_moving_duration / 60:.2f} minutes")
    print(f"Total PUSH_UP reps since {start_date}: {pushups}")
    print(f"Total PULL_UP reps since {start_date}: {pullups}")
    # # Print results
    # for tag, total in results.items():
    #     print(f"Total {tag} ({tag_parameters[tag]}): {total:.2f}")
    
    
    # Print results
    for description, total in results.items():
        print(f"Total {description}: {total:.2f}")


if __name__ == "__main__":
    main()
