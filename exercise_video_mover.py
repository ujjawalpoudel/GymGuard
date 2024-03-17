import os
import json
import shutil
from src.project_root_locator import find_project_root

# Find the project's root directory
project_root = find_project_root()

# List of exercise filenames
exercise_filenames = [
    "band_pull_apart.mp4",
    "barbell_dead_row.mp4",
    "barbell_row.mp4",
    "barbell_shrug.mp4",
    "burpees.mp4",
    "clean_and_press.mp4",
    "deadlift.mp4",
    "diamond_pushup.mp4",
    "drag_curl.mp4",
    "dumbbell_biceps_curls.mp4",
    "dumbbell_curl_trifecta.mp4",
    "dumbbell_hammer_curls.mp4",
    "dumbbell_high_pulls.mp4",
    "dumbbell_overhead_shoulder_press.mp4",
    "dumbbell_reverse_lunge.mp4",
    "dumbbell_scaptions.mp4",
    "man_maker.mp4",
    "mule_kick.mp4",
    "neutral_overhead_shoulder_press.mp4",
    "one_arm_row.mp4",
    "overhead_extension_thruster.mp4",
    "overhead_trap_raises.mp4",
    "pushup.mp4",
    "side_lateral_raise.mp4",
    "squat.mp4",
    "standing_ab_twists.mp4",
    "w_raise.mp4",
    "walk_the_box.mp4",
]

# Main folder where data is stored
main_folder_name = "train"

# Dictionary containing exercise name and corresponding folder name
exercise_info = {}

# Inform the user about the start of processing
print("Processing exercise videos...")

# Loop through each exercise filename
for exercise_filename in exercise_filenames:
    # Inform the user about the current exercise being processed
    print("Processing exercise:", exercise_filename)

    # Extract the exercise name without the file extension
    exercise_name = os.path.splitext(exercise_filename)[0]

    # Define the destination folder for the exercise videos
    destination_folder = os.path.join(
        project_root, "data", main_folder_name, exercise_name
    )

    # Select all subfolders in the training folder starting with 's'
    subfolders = [
        f.path
        for f in os.scandir(main_folder_name)
        if f.is_dir() and f.name.startswith("s")
    ]

    # Loop through each subfolder
    for folder_path in subfolders:
        # Inform the user about the current folder being processed
        print("Processing folder:", folder_path)
        person_name = os.path.basename(
            folder_path
        )  # Extract the person's name from the folder path
        videos_folder = os.path.join(folder_path, "videos")

        # Check if the videos folder exists in the current folder
        if not os.path.exists(videos_folder):
            continue

        # List of folders to search within the videos folder
        folders_to_search = ["65906101", "60457274"]

        # Loop through each folder to search within the videos folder
        for search_folder_name in folders_to_search:
            # Inform the user about the current folder being searched
            print("Searching in folder:", search_folder_name)
            src_file_path = os.path.join(
                project_root, videos_folder, search_folder_name, exercise_filename
            )
            # Inform the user about the source file path
            print("Source file path:", src_file_path)

            # Check if the exercise video file exists in the current folder
            if os.path.exists(src_file_path):
                # Create the destination folder if it doesn't exist
                if not os.path.exists(destination_folder):
                    os.makedirs(destination_folder)
                    # Inform the user about the creation of the destination folder
                    print("Created destination folder:", destination_folder)

                # Generate a new filename for the destination file
                new_filename = (
                    f"{exercise_name}_{search_folder_name}_{person_name}_13ang.mp4"
                )
                dest_file_path = os.path.join(destination_folder, new_filename)
                # Inform the user about the destination file path
                print("Destination file path:", dest_file_path)

                # Add exercise name to the dictionary
                exercise_info[new_filename] = exercise_filename.split(".")[0]

                # Move the exercise video file to the destination folder with the new filename
                shutil.move(src_file_path, dest_file_path)
                # Inform the user about the movement of the exercise video file
                print(f"Moved {exercise_filename} to {dest_file_path}")
                print("\n")

# Inform the user about the completion of the process
print("Exercise video processing completed.")

# Path to the exercise names JSON file
json_file_path = os.path.join(project_root, "exercise_names.json")

# Load existing JSON data from exercise_names.json
existing_data = {}
if os.path.exists(json_file_path):
    with open(json_file_path, "r") as json_file:
        existing_data = json.load(json_file)

# Update existing JSON data with new exercise information
for key, value in exercise_info.items():
    if key not in existing_data:
        existing_data[key] = value
        # Inform the user about the addition of exercise data to the JSON file
        print(f"Added {key}: {value} to the exercise names JSON file.")
    else:
        # Inform the user if exercise data already exists in the JSON file
        print(f"The key {key} already exists in the exercise names JSON file.")

# Save the updated dictionary back to the JSON file
with open(json_file_path, "w") as json_file:
    json.dump(existing_data, json_file, indent=4)

# Inform the user about the completion of the update process
print("Exercise names JSON file updated successfully.")
