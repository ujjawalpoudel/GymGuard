import os
import json
import ast
import pandas as pd
import numpy as np

from utils.csv_file_pair_finder import find_csv_file_pairs_in_folder
from utils.exercise_velocity_data import update_json_file


class AngularVelocityCalculator:
    """
    A class to calculate angular velocity from annotated CSV data.

    Attributes:
        filename (str): The name of the video file.
        filepath (str): The path to the annotated CSV file.
        window_size (int, optional): The size of the window for peak detection. Defaults to 100.
        results (dict): A dictionary to store calculated results.
    """

    def __init__(self, filename, filepath, window_size=100):
        """
        Initialize AngularVelocityCalculator with the specified parameters.

        Args:
            filename (str): The name of the video file.
            filepath (str): The path to the annotated CSV file.
            window_size (int, optional): The size of the window for peak detection. Defaults to 100.
        """
        self.window_size = window_size
        self.filename = filename
        self.filepath = filepath
        self.results = {}

    def calculate_angular_velocity(self, all_angle_indices):
        """
        Calculate angular velocity based on annotated CSV data.

        Args:
            all_angle_indices (list): List of frame indices with annotated data.
        """
        # Read annotated CSV data
        df = pd.read_csv(self.filepath)
        # Convert string representations of lists to actual lists
        df["data"] = df["data"].apply(ast.literal_eval)

        coordinates = []
        timestamps = []
        all_angle_indices.insert(0, 0)  # Include frame 0 in all_angle_indices

        # Extract coordinates and timestamps from annotated data
        for frame_number in all_angle_indices:
            row = df[df["frame"] == frame_number]
            data_column = row["data"].iloc[0]
            coordinates.append(
                [data_column[-1]["x"], data_column[-1]["y"], data_column[-1]["z"]]
            )
            timestamps.append(data_column[-1]["time"])

        angular_velocities = []
        # Calculate angular velocity between consecutive frames
        for i in range(len(coordinates) - 1):
            coord_current, coord_next = coordinates[i], coordinates[i + 1]
            timestamp_current, timestamp_next = timestamps[i], timestamps[i + 1]
            displacement = np.array(coord_next) - np.array(coord_current)
            delta_t = timestamp_next - timestamp_current
            displacement_magnitude = np.linalg.norm(displacement)
            angular_velocity = displacement_magnitude / delta_t
            angular_velocities.append(angular_velocity)

        # Remove NaN values
        angular_velocities = [x for x in angular_velocities if not np.isnan(x)]

        # Sort the list
        sorted_angular_velocities = sorted(angular_velocities)

        # Calculate median
        median_index = len(sorted_angular_velocities) // 2
        median = sorted_angular_velocities[median_index]

        # Split data into two clusters based on median
        min_cluster = [x for x in sorted_angular_velocities if x <= median]
        max_cluster = [x for x in sorted_angular_velocities if x > median]

        # Find maximum in minimum cluster and minimum in maximum cluster
        max_in_min_cluster = max(max_cluster)
        min_in_max_cluster = min(min_cluster)

        # Store results in class attribute
        self.results["exercise_name"] = self.filename
        self.results["max_velocity"] = max_in_min_cluster
        self.results["min_velocity"] = min_in_max_cluster

    def save_results_to_json(self, output_file):
        """
        Save calculated results to a JSON file.

        Args:
            output_file (str): The path to save the JSON file.
        """
        with open(output_file, "w") as json_file:
            json.dump(self.results, json_file, indent=4)


def main():
    # Find pairs of CSV files
    csv_pairs = find_csv_file_pairs_in_folder()

    max_angular_velocity = []
    min_angular_velocity = []

    for csv_file, annotated_file in csv_pairs.items():
        print(f"CSV file: {csv_file}, Annotated file: {annotated_file}")

        if not os.path.exists(csv_file):
            print(f"Error: CSV file not found at path {csv_file}")
            continue

        if not os.path.exists(annotated_file):
            print(f"Error: CSV file not found at path {annotated_file}")
            continue

        # Read CSV data and extract indices
        df = pd.read_csv(csv_file)
        df["indices"] = df["indices"].apply(ast.literal_eval)
        indices_list = [item for sublist in df["indices"].tolist() for item in sublist]
        indices_list_sorted = sorted(indices_list)

        # Calculate angular velocity and save results
        calculator = AngularVelocityCalculator("dumbbell_biceps_curls", annotated_file)
        calculator.calculate_angular_velocity(indices_list_sorted)

        # Append in list
        max_angular_velocity.append(calculator.results["max_velocity"])
        min_angular_velocity.append(calculator.results["min_velocity"])
        print("\n")

    # Calculate average value of angular velocity
    max_angular_velocity_value = sum(max_angular_velocity) / len(max_angular_velocity)
    min_angular_velocity_value = sum(min_angular_velocity) / len(min_angular_velocity)

    update_json_file(
        "angular_velocity_results.json",
        "dumbbell_biceps_curls",
        max_angular_velocity_value,
        min_angular_velocity_value,
    )


if __name__ == "__main__":
    main()
