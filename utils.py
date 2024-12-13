import platform
import subprocess

# Utility function to split text into chunks
def split_text(text, chunk_size=2900):
    """
    Splits the input text into smaller chunks of a specified size.

    Parameters:
    - text (str): The text to be split.
    - chunk_size (int): The maximum size of each chunk.

    Returns:
    - list: A list of text chunks.
    """
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]


def open_file_with_default_app(file_path):
    """Open a file with the system's default application."""
    try:
        if platform.system() == "Windows":
            subprocess.run(["start", file_path], check=True, shell=True)
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", file_path], check=True)
        elif platform.system() == "Linux":
            subprocess.run(["xdg-open", file_path], check=True)
        else:
            raise RuntimeError("Unsupported operating system")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Could not open file: {e}")
