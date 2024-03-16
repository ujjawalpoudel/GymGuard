import os
import shutil
from src.project_root_locator import find_project_root

# Find the project's root directory
project_root = find_project_root()

# Define the list of exercise filenames
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

# Define the main folder where data is stored
main_folder_name = "train"

# Loop through each exercise filename
for exercise_filename in exercise_filenames:
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
            print("Searching in folder:", search_folder_name)
            src_file_path = os.path.join(
                project_root, videos_folder, search_folder_name, exercise_filename
            )
            print("Source file path:", src_file_path)

            # Check if the exercise video file exists in the current folder
            if os.path.exists(src_file_path):
                # Create the destination folder if it doesn't exist
                if not os.path.exists(destination_folder):
                    os.makedirs(destination_folder)
                    print("Created destination folder:", destination_folder)

                # Generate a new filename for the destination file
                new_filename = (
                    f"{exercise_name}_{search_folder_name}_{person_name}_13ang.mp4"
                )
                dest_file_path = os.path.join(destination_folder, new_filename)
                print("Destination file path:", dest_file_path)

                # Move the exercise video file to the destination folder with the new filename
                shutil.move(src_file_path, dest_file_path)
                print(f"Moved {exercise_filename} to {dest_file_path}")
                print("\n")
