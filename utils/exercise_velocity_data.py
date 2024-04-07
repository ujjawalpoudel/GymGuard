import json
import os


def update_json_file(file_name, exercise_name, new_max_velocity, new_min_velocity, joint_angle):
    """
    Update max_velocity and min_velocity values for a specific exercise in a JSON file.

    Args:
        file_name (str): Name of the JSON file to update.
        exercise_name (str): Name of the exercise to update.
        new_max_velocity (float): New value for max_velocity.
        new_min_velocity (float): New value for min_velocity.
        joint_angle (str): Name of the joint angle.
    """
    # Check if the JSON file exists
    if not os.path.exists(file_name):
        # If the file doesn't exist, create a new dictionary
        data = {}
    else:
        # Open and read the existing JSON file
        with open(file_name, "r") as json_file:
            data = json.load(json_file)

    # Update values for the exercise
    exercise_data = data.setdefault(exercise_name, {})
    exercise_data[joint_angle] = {
        "max_velocity": new_max_velocity,
        "min_velocity": new_min_velocity,
    }

    # Write the updated data back to the JSON file
    with open(file_name, "w") as json_file:
        json.dump(data, json_file, indent=4)
