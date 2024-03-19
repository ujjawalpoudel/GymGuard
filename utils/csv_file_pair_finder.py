import os
from src.project_root_locator import find_project_root


def find_csv_file_pairs_in_folder():
    """
    Find pairs of CSV files in the 'data/output_csv' folder.

    This function searches for CSV files in the 'data/output_csv' folder,
    where each pair consists of a file with 'angle_peaks' in its name
    and its corresponding annotated file with 'annotated' in its name.

    Returns:
        dict: A dictionary where keys are names of CSV files with 'angle_peaks'
        and values are the corresponding annotated CSV file names.

    Example:
        >>> find_csv_file_pairs_in_folder()
        {'data.csv': 'annotated_data.csv', 'results.csv': 'annotated_results.csv'}
    """
    # Get project root folder
    project_root = find_project_root()

    # Join the project root folder with the folder containing CSV files
    csv_folder_path = os.path.join(project_root, "data", "output_csv")

    # Dictionary to store CSV file pairs
    csv_file_pairs = {}

    # Iterate over all files in the folder
    for csv_file in os.listdir(csv_folder_path):
        # join the CSV file with the project root
        csv_file = os.path.join(csv_folder_path, csv_file)

        # Check if the file ends with '.csv'
        if csv_file.endswith(".csv"):
            if "angle_peaks" in csv_file:
                # Create the corresponding annotated file name
                annotated_csv_file = csv_file.replace("angle_peaks", "annotated")
                # Store the pair in the dictionary
                csv_file_pairs[csv_file] = annotated_csv_file

    return csv_file_pairs
