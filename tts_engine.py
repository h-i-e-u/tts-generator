from tkinter import filedialog
import edge_tts
import os
from utils import open_file_with_default_app, split_text


# Process text to speech with handling for large inputs
async def process_text_to_speech(text, voice, output_file, progress_callback=None, status_callback=None, is_cancelled=None):
    try:
        chunks = split_text(text, 2900)  # Split the text into manageable chunks
        temp_files = []

        # Process each chunk
        for idx, chunk in enumerate(chunks):
            if is_cancelled and is_cancelled():
                break  # Exit if the operation is cancelled

            temp_file = f"chunk_{idx}.mp3"
            tts = edge_tts.Communicate(chunk, voice)
            await tts.save(temp_file)
            temp_files.append(temp_file)

            # Update progress
            if progress_callback:
                progress_callback((idx + 1) / len(chunks))
            
            # Update status with current chunk
            if status_callback:
                status_callback(f"Processing chunk {idx + 1} of {len(chunks)}")

        # Merge all chunks into a single output file if not cancelled
        if not is_cancelled or not is_cancelled():
            with open(output_file, "wb") as final_file:
                for temp_file in temp_files:
                    if is_cancelled and is_cancelled():
                        break  # Exit if the operation is cancelled
                    with open(temp_file, "rb") as f:
                        final_file.write(f.read())
                    os.remove(temp_file)  # Clean up temporary files
    except Exception as e:
        raise RuntimeError(f"Error processing TTS: {e}")

# Play audio file
def play_audio(file_path=None):
    """Play an audio file using the system's default audio player."""
    if not file_path:
        file_path = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=[("MP3 Files", "*.mp3"), ("All Files", "*.*")]
        )
    if not file_path:
        return

    try:
        open_file_with_default_app(file_path)
    except RuntimeError as e:
        raise RuntimeError(f"Could not play audio: {e}")
