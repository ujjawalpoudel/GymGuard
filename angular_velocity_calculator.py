import os
import json
import ast
import pandas as pd
import numpy as np
import math

from utils.csv_file_pair_finder import find_csv_file_pairs_in_folder
from utils.exercise_velocity_data import update_json_file


class AngularVelocityCalculator:
    """
    A class to calculate angular velocity from annotated CSV data.

    Attributes:
        window_size (int, optional): The size of the window for peak detection. Defaults to 100.
        filename (str): The name of the video file.
        filepath (str): The path to the annotated CSV file.
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

    def calculate_angular_velocity(self, all_frame_indices, single_changing_index):
        """
        Calculate angular velocity based on annotated CSV data.

        Args:
            all_frame_indices (list): List of frame indices with annotated data.
            single_changing_index (str): Name of the column containing single changing index.
        """
        # Read annotated CSV data
        df = pd.read_csv(self.filepath)

        angles = []
        timestamps = []
        all_frame_indices.insert(0, 1)  # Include frame 1 in all_frame_indices

        # Extract angles and timestamps from annotated data
        for frame_number in all_frame_indices:
            row = df[df["frame"] == frame_number]
            angles.append(row[single_changing_index].iloc[0])
            timestamps.append(row["timestamp"].iloc[0])

        angular_velocities = []
        # Calculate angular velocity between consecutive frames
        for i in range(len(angles) - 1):
            angle_current, angle_next = angles[i], angles[i + 1]
            timestamp_current, timestamp_next = timestamps[i], timestamps[i + 1]
            
            # Convert angles from degrees to radians
            theta1_rad = math.radians(angle_current)
            theta2_rad = math.radians(angle_next)
            
            # Calculate change in angle
            delta_theta = theta2_rad - theta1_rad
            
            # Calculate change in time
            delta_t = timestamp_next - timestamp_current
            
            # Calculate average angular velocity
            average_angular_velocity = delta_theta / delta_t
            
            angular_velocities.append(average_angular_velocity)
            
        # Remove NaN values
        angular_velocities = [x for x in angular_velocities if not np.isnan(x)]

        # Sort the list
        sorted_angular_velocities = sorted(angular_velocities)

        if len(sorted_angular_velocities) > 2:
            # Calculate median
            median_index = len(sorted_angular_velocities) // 2
            median = sorted_angular_velocities[median_index]

            # Split data into two clusters based on median
            min_cluster = [x for x in sorted_angular_velocities if x <= median]
            max_cluster = [x for x in sorted_angular_velocities if x > median]

            # Find maximum in minimum cluster and minimum in maximum cluster
            max_in_min_cluster = max(max_cluster)
            min_in_max_cluster = min(min_cluster)
        else:
            max_in_min_cluster = max(sorted_angular_velocities)
            min_in_max_cluster = min(sorted_angular_velocities)

        # Store results in class attribute
        self.results["exercise_name"] = self.filename
        self.results["joint_angle"] = single_changing_index
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

    max_angular_velocities = []
    min_angular_velocities = []

    for csv_file, annotated_file in csv_pairs.items():
        print(f"CSV file: {csv_file}, Annotated file: {annotated_file}")
        print("\n====================================\n")

        if not os.path.exists(csv_file):
            print(f"Error: CSV file not found at path {csv_file}")
            continue

        if not os.path.exists(annotated_file):
            print(f"Error: CSV file not found at path {annotated_file}")
            continue

        df = pd.read_csv(csv_file)
        df["indices"] = df["indices"].apply(ast.literal_eval)

        # Get single changing indices
        single_indices = df["column"][0]

        indices_list = [item for sublist in df["indices"].tolist() for item in sublist]
        indices_list_sorted = sorted(indices_list)

        # Calculate angular velocity and save results
        calculator = AngularVelocityCalculator("dumbbell_biceps_curls", annotated_file)
        calculator.calculate_angular_velocity(indices_list_sorted, single_indices)

        # Append in list
        max_angular_velocities.append(calculator.results["max_velocity"])
        min_angular_velocities.append(calculator.results["min_velocity"])

    # Calculate average value of angular velocity
    max_angular_velocity_value = sum(max_angular_velocities) / len(max_angular_velocities)
    min_angular_velocity_value = sum(min_angular_velocities) / len(min_angular_velocities)

    update_json_file(
        "angular_velocity_results.json",
        "dumbbell_biceps_curls",
        max_angular_velocity_value,
        min_angular_velocity_value,
        calculator.results["joint_angle"],
    )


if __name__ == "__main__":
    main()
