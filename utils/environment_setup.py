import os
from dotenv import load_dotenv


def clear_and_load_env():
    """
    Clears all environment variables and loads new ones from the .env file.

    Returns:
    - bool: True if successful, False otherwise.
    """
    try:
        # Clear existing environment variables
        for key in list(os.environ):
            del os.environ[key]

        # Load new environment variables from .env file
        load_dotenv()

        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
