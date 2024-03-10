import os

from src.project_root_locator import find_project_root
from src.pose_landmark_extractor import PoseLandmarkExtractor
from utils.check_file_existence import check_file_existence
from src.angle_peak_detector import AnglePeaksDetector
from utils.image_cleanup import cleanup_temp_images
from utils.file_listing import list_video_files
from utils.environment_setup import clear_and_load_env


def initialize_pose_extractor(project_root_path, video_file_name, video_path):
    """
    Initialize the PoseLandmarkExtractor instance with required parameters.

    Args:
        project_root_path (str): The root path of the project.
        video_file_name (str): The name of the video file.
        video_path (str): The path of the video file.

    Returns:
    - tuple: (PoseLandmarkExtractor instance, success flag).
    """
    try:
        if video_file_name is None:
            print("Error: No environment variable named VIDEO_FILE_NAME found.")
            return None, False

        if check_file_existence(video_path):
            # Create an instance of the PoseLandmarkExtractor class
            pose_extractor = PoseLandmarkExtractor(
                video_file_name, project_root_path, video_path
            )
            return pose_extractor, True
        else:
            print("Error: Input video file not found.")
            print(f"Path: {video_path}")
            return None, False
    except Exception as e:
        print(f"Error initializing PoseLandmarkExtractor: {e}")
        return None, False


def main():
    """
    Main function to run the pose landmark extraction process.
    """
    try:
        # Load environment variables
        if not clear_and_load_env():
            print("Error: Failed to load environment variables.")
            return

        # Find project root directory
        project_root_path = find_project_root()

        # Load environment variables
        root_directory = os.getenv("ROOT_DIRECTORY")

        # List all video files in the input_videos directory
        video_files_list = list_video_files(root_directory, project_root_path)

        for video_path in video_files_list:
            print(f"Now processing video: {video_path}")

            # Extract file name from video_path
            video_file_name = os.path.basename(video_path)

            print("Extracted file name:", video_file_name)

            # Initialize PoseLandmarkExtractor
            pose_extractor, success = initialize_pose_extractor(
                project_root_path, video_file_name, video_path
            )
            if not success or pose_extractor is None:
                print("Error: Failed to initialize PoseLandmarkExtractor.")
                return

            # Run the pose landmark extraction process
            pose_extractor.run_extraction()
            print("Success: Pose landmark extraction completed.")

            # Calculate angle peak values
            detector = AnglePeaksDetector(video_file_name)
            angle_peaks, all_angle_indices = detector.find_angle_peaks()

            # Delete all images except for all_angle_indices
            cleanup_temp_images(all_angle_indices)
            print("Success: Temporary images cleaned up.")

            print("Success: Angle peak values calculated.")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    # Call the main function
    main()
