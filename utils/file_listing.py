import os


def list_video_files(root_directory, project_root_path):
    """
    Recursively lists all video file names in the specified directory and its subdirectories.

    Args:
        root_directory (str): The root directory to search for files.
        project_root_path (str): The root path of the project.

    Returns:
        list: A list containing all video file names found.
    """
    # Initialize an empty list to store video file names
    video_files = []

    # Known video file extensions
    video_extensions = [".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv", ".webm"]

    # Recursively iterate over all files and directories in the root directory
    for root, dirs, files in os.walk(root_directory):
        # Iterate over each file in the current directory
        for file in files:
            # Check if the file has a video extension
            _, file_extension = os.path.splitext(file)
            if file_extension.lower() in video_extensions:
                # Construct the full path of the file
                file_path = os.path.join(project_root_path, root, file)
                # Add the video file name to the list
                video_files.append(file_path)

    return video_files
