import cv2
import math
import mediapipe as mp
import pandas as pd
import numpy as np
import json
from utils.joint_angle_calculator import calculate_joint_angles
from scipy.signal import argrelextrema


def retrieve_velocity_data(exercise_name, file_path):
    """
    Retrieve max and min velocity data for a given exercise from a JSON file.

    Args:
        exercise_name (str): The name of the exercise.
        file_path (str): The path to the JSON file containing velocity data.

    Returns:
        tuple: A tuple containing the max and min velocity for the exercise.
    """
    with open(file_path, "r") as json_file:
        data = json.load(json_file)
        if exercise_name in data:
            exercise_data = data[exercise_name]
            joint_angle, velocity_info = exercise_data.popitem()
            max_velocity = velocity_info.get("max_velocity")
            min_velocity = velocity_info.get("min_velocity")
            return max_velocity, min_velocity, joint_angle
        else:
            return None, None, None


def process_video(video_path, exercise_name, file_path):
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

            for idx, landmark in enumerate(landmarks):
                frame_time = frame_count / fps

                if idx == 32:
                    temp_pose_data.append(frame_time)
                    temp_pose_data.append(frame_count)
                    temp_pose_data.extend(list(angle_of_joint.values()))
                    pose_data_list.append(temp_pose_data)
                    temp_pose_data = []

        cv2.imshow("Video", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

        if frame_count == 200:
            if not analyze_pose_data(pose_data_list, exercise_name, file_path):
                raise ValueError
            pose_data_list = []
            frame_count = 0

    cap.release()
    cv2.destroyAllWindows()


def analyze_pose_data(pose_data_list, exercise_name, file_path):
    """
    Analyze pose data, calculate velocities, and compare with predefined thresholds.

    Args:
        pose_data_list (list): A list of pose data.

    Returns:
        bool: True if analysis is successful, False otherwise.
    """
    column_names = [
        "timestamp",
        "frame",
    ]

    # JOINTS_NAME : Name of the joints which we track for angle
    JOINTS_NAME = [
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

    # Extend column name
    column_names.extend(JOINTS_NAME)

    df = pd.DataFrame(pose_data_list, columns=column_names)

    df[JOINTS_NAME] = df[JOINTS_NAME].rolling(window=90, min_periods=1).mean()

    max_velocity, min_velocity, joint_angle = retrieve_velocity_data(
        exercise_name, file_path
    )

    all_angle_indices = [1]
    y = df[joint_angle].values
    peaks_indices = argrelextrema(y, np.greater, order=100)[0]
    valleys_indices = argrelextrema(y, np.less, order=100)[0]
    apex_indices = np.sort(np.concatenate([peaks_indices, valleys_indices]))

    all_angle_indices.extend([int(x) for x in apex_indices])

    angles = []
    timestamps = []

    # Extract angles and timestamps from annotated data
    for frame_number in all_angle_indices:
        row = df[df["frame"] == frame_number]
        angles.append(row[joint_angle].iloc[0])
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

    current_max_velocity, current_min_velocity = max(angular_velocities), min(
        angular_velocities
    )

    if max_velocity is not None and min_velocity is not None:
        print(
            f"For exercise '{exercise_name}':\nAverage Max Velocity: {max_velocity}\nAverage Min Velocity: {min_velocity}\n"
        )

        if current_max_velocity > max_velocity:
            print("Warning: Slow down your movements a bit, you're moving pretty fast")
        elif current_min_velocity < min_velocity:
            print("Warning: Speed up your movements a bit, you're going a bit slow.")
        else:
            print("Great job! Your movement speed is optimal.")

        print(
            f"Current Max Velocity: {current_max_velocity}\nCurrent Min Velocity: {current_min_velocity}"
        )
    else:
        print(f"No data found for exercise '{exercise_name}'")

    return True


if __name__ == "__main__":
    video_path = (
        "data/train/dumbbell_biceps_curls/dumbbell_biceps_curls_60457274_s03_13ang.mp4"
    )
    exercise_name = "dumbbell_biceps_curls"
    file_path = "angular_velocity_results.json"
    process_video(video_path, exercise_name, file_path)
