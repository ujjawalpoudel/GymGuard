import json
import os


def update_json_file(file_name, exercise_name, new_max_velocity, new_min_velocity):
    """
    Update the values of max_velocity and min_velocity for a specific exercise in a JSON file.

    Args:
        file_name (str): The name of the JSON file to be updated.
        exercise_name (str): The name of the exercise to be updated.
        new_max_velocity (float): The new value for max_velocity.
        new_min_velocity (float): The new value for min_velocity.
    """
    # Check if the JSON file exists
    if not os.path.exists(file_name):
        # If file does not exist, create a new dictionary
        data = {}
    else:
        # Open and read the existing JSON file
        with open(file_name, "r") as json_file:
            data = json.load(json_file)

    # Update the values for the exercise
    data[exercise_name] = {
        "max_velocity": new_max_velocity,
        "min_velocity": new_min_velocity,
    }

    # Write the updated data back to the JSON file
    with open(file_name, "w") as json_file:
        json.dump(data, json_file, indent=4)
