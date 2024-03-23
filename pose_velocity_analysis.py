import cv2
import mediapipe as mp
import pandas as pd
import numpy as np
import json
from utils.joint_angle_calculator import calculate_joint_angles
from scipy.signal import argrelextrema
from constant import JOINTS_NAME


def get_velocity_data(exercise_name, file_path):
    """
    Retrieve max and min velocity data for a given exercise from a JSON file.

    Args:
        exercise_name (str): The name of the exercise.
        file_path (str): The path to the JSON file containing velocity data.

    Returns:
        tuple: A tuple containing the max and min velocity for the exercise.
    """
    with open(file_path, "r") as file:
        data = json.load(file)
        if exercise_name in data:
            exercise_data = data[exercise_name]
            return exercise_data.get("max_velocity"), exercise_data.get("min_velocity")
        else:
            return None, None


def process_video(video_path):
    """
    Process the input video, extract pose data, and calculate velocities.

    Args:
        video_path (str): The path to the input video.

    Returns:
        None
    """
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()
    mp_drawing = mp.solutions.drawing_utils

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = 0
    pose_data_list = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frame_rgb)

        if results.pose_landmarks:
            mp_drawing.draw_landmarks(
                frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS
            )
            temp_pose_data = []
            landmarks = results.pose_landmarks.landmark
            angle_of_joint = calculate_joint_angles(landmarks)

            # Append pose data
            for idx, landmark in enumerate(landmarks):
                frame_time = frame_count / fps
                temp_pose_data.append(
                    {
                        "x": landmark.x,
                        "y": landmark.y,
                        "z": landmark.z,
                        "visibility": landmark.visibility,
                        "landmark": idx,
                        "time": frame_time,
                        "frame_index": frame_count,
                    }
                )

                if idx == 32:
                    temp_pose_data = [temp_pose_data]
                    temp_pose_data.append(frame_count)
                    temp_pose_data.extend(list(angle_of_joint.values()))
                    pose_data_list.append(temp_pose_data)
                    temp_pose_data = []

        cv2.imshow("Video", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

        if frame_count == 200:
            if not analyze_pose_data(pose_data_list):
                raise ValueError
            pose_data_list = []
            frame_count = 0

    cap.release()
    cv2.destroyAllWindows()


def analyze_pose_data(pose_data_list):
    """
    Analyze pose data, calculate velocities, and compare with predefined thresholds.

    Args:
        pose_data_list (list): A list of pose data.

    Returns:
        bool: True if analysis is successful, False otherwise.
    """
    column_names = [
        "data",
        "frame",
        "left_arm",
        "right_arm",
        "left_elbow",
        "right_elbow",
        "left_waist_leg",
        "right_waist_leg",
        "left_knee",
        "right_knee",
        "leftup_chest_inside",
        "rightup_chest_inside",
        "leftlow_chest_inside",
        "rightlow_chest_inside",
        "leg_spread",
    ]

    df = pd.DataFrame(pose_data_list, columns=column_names)

    df[JOINTS_NAME] = df[JOINTS_NAME].rolling(window=90, min_periods=1).mean()

    deviation_percentage = (
        (df.iloc[:, 3:].max() - df.iloc[:, 3:].min()) / df.iloc[:, 3:].mean()
    ) * 100
    sorted_columns = deviation_percentage.sort_values(ascending=False)
    num_columns_to_consider = 1
    column_with_highest_deviation = sorted_columns.index[:num_columns_to_consider]

    all_angle_indices = [df.iloc[0]["frame"]]
    for col in column_with_highest_deviation:
        y = df[col].values
        peaks_indices = argrelextrema(y, np.greater, order=100)[0]
        valleys_indices = argrelextrema(y, np.less, order=100)[0]
        apex_indices = np.sort(np.concatenate([peaks_indices, valleys_indices]))
        all_angle_indices.extend([int(x) for x in apex_indices])

    all_angle_indices.append(df.iloc[-1]["frame"])
    all_angle_indices.sort()

    coordinates = []
    timestamps = []
    for frame_number in all_angle_indices:
        row = df[df["frame"] == frame_number]
        data_column = row["data"].iloc[0]
        coordinates.append(
            [data_column[-1]["x"], data_column[-1]["y"], data_column[-1]["z"]]
        )
        timestamps.append(data_column[-1]["time"])

    angular_velocities = []
    for i in range(len(coordinates) - 1):
        coord_current, coord_next = coordinates[i], coordinates[i + 1]
        timestamp_current, timestamp_next = timestamps[i], timestamps[i + 1]
        displacement = np.array(coord_next) - np.array(coord_current)
        delta_t = timestamp_next - timestamp_current
        displacement_magnitude = np.linalg.norm(displacement)
        angular_velocity = displacement_magnitude / delta_t
        angular_velocities.append(angular_velocity)

    current_max_velocity, current_min_velocity = max(angular_velocities), min(
        angular_velocities
    )

    exercise_name = "dumbbell_biceps_curls"
    file_path = "angular_velocity_results.json"
    max_velocity, min_velocity = get_velocity_data(exercise_name, file_path)

    if max_velocity is not None and min_velocity is not None:
        print("\n")
        print(
            f"For exercise '{exercise_name}':\nAverage Max Velocity: {max_velocity}\nAverage Min Velocity: {min_velocity}\n"
        )

        if current_max_velocity > max_velocity:
            print("Warning: Slow down your movements a bit, you're moving pretty fast")
        elif current_min_velocity < min_velocity:
            print("Warning: Speed up your movements a bit, you're going a bit slow.")
        else:
            print("Great job! Your movement speed is optimal.")

        print("\n")
        print(
            f"Current Max Velocity: {current_max_velocity}\nCurrent Min Velocity: {current_min_velocity}"
        )
    else:
        print(f"No data found for exercise '{exercise_name}'")

    print("\n")
    return True


if __name__ == "__main__":
    video_path = "/Users/ujjawalpoudel/Downloads/dumbbell_biceps_curls_s13.MP4"
    process_video(video_path)
