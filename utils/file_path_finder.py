import os
from src.project_root_locator import find_project_root


def find_annotated_csv_path(video_file_name):
    """
    Find the path of the annotated CSV file based on the given video file name.

    Args:
        video_file_name (str): The name of the video file.

    Returns:
        tuple: A tuple containing a boolean indicating the success status and the output CSV path.
    """
    try:
        # Extract file name without extension
        file_name = os.path.splitext(video_file_name)[0]

        # Define the path to the annotated CSV file
        annotated_csv_path = os.path.join(
            find_project_root(), "data", "output_csv", f"annotated_{file_name}.csv"
        )

        # Check if the file exists
        if os.path.exists(annotated_csv_path):
            # Return success status and the CSV path if the file exists
            return True, annotated_csv_path
        else:
            # Return failure status and None if the file doesn't exist
            return False, None
    except Exception as e:
        # Handle any exception gracefully and return failure status and None
        print(f"An error occurred: {e}")
        return False, None
