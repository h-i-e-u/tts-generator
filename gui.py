import customtkinter
from tkinter import filedialog, messagebox
import asyncio
from tts_engine import process_text_to_speech, play_audio
import threading

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("TTS - Speech Generator")
        self.geometry("800x400")
        self.grid_columnconfigure(0, weight=1)

        # Initialize variables
        self.selected_voice = "en-US-JennyNeural"
        self.cancelled = False  # Add a cancellation flag
        self.generating_status = False  # Flag to control the blinking status

        # Create frames
        self.create_frames()

        # Add widgets to frames
        self.add_widgets_to_bar_frame()
        self.add_widgets_to_left_frame()
        self.add_widgets_to_right_frame()
        self.add_widgets_to_bottom_frame()

        self.status_label = self.bottom_label  # Rename for clarity

    def create_frames(self):
        """Create and configure frames."""
        self.bar_frame = customtkinter.CTkFrame(self, corner_radius=10, height=60, width=800)
        self.bar_frame.grid(row=0, column=0, sticky="new")

        self.main_frame = customtkinter.CTkFrame(self, corner_radius=10, height=300, width=800)
        self.main_frame.grid(row=1, column=0, sticky="ew")

        self.bottom_frame = customtkinter.CTkFrame(self, corner_radius=10, height=40, width=800)
        self.bottom_frame.grid(row=2, column=0, sticky="ew")

        # Split the main frame into two frames
        self.left_frame = customtkinter.CTkFrame(self.main_frame, corner_radius=10, height=300)
        self.left_frame.pack(side="left", fill="both", expand=True)

        self.right_frame = customtkinter.CTkFrame(self.main_frame, corner_radius=10, height=300, width=300)
        self.right_frame.pack(side="right", fill="both")

    def add_widgets_to_bar_frame(self):
        """Add widgets to the bar frame."""
        self.bar_label = customtkinter.CTkLabel(self.bar_frame, text="Speech Generator", font=("Arial", 22, "bold"))
        self.bar_label.pack(side="left", fill="both", padx=10, pady=10, expand=True)

        self.theme_selector = customtkinter.CTkOptionMenu(self.bar_frame, values=["Light", "Dark", "System"], command=self.change_theme)
        self.theme_selector.pack(side="right", fill="both", padx=10, pady=10)

    def add_widgets_to_left_frame(self):
        """Add widgets to the left frame."""
        self.left_label = customtkinter.CTkLabel(self.left_frame, text="Enter Text", font=("Arial", 22))
        self.left_label.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        self.textbox = customtkinter.CTkTextbox(self.left_frame, height=200, width=600, border_width=2, border_color="#000000")
        self.textbox.pack(side="bottom", fill="both", expand=True, padx=10, pady=10)
        self.textbox.bind("<KeyRelease>", lambda event: self.update_word_count())

    def add_widgets_to_right_frame(self):
        """Add widgets to the right frame."""
        self.generate_button = customtkinter.CTkButton(self.right_frame, text="Generate", font=("Arial", 12), command=self.generate_tts)
        self.generate_button.grid(row=0, column=0, padx=10, pady=(60, 10))

        self.play_button = customtkinter.CTkButton(self.right_frame, text="Play", font=("Arial", 12), command=self.play_audio, state="disabled")
        self.play_button.grid(row=1, column=0, padx=10, pady=10)

        self.voice_selector = customtkinter.CTkOptionMenu(self.right_frame, values=[
            "en-US-JennyNeural",
            "en-US-GuyNeural",
            "en-GB-LibbyNeural",
            "en-GB-RyanNeural"
        ], command=self.select_voice)
        self.voice_selector.grid(row=2, column=0, padx=10, pady=10)
        self.voice_selector.set("en-US-JennyNeural")  # Set default voice

    def add_widgets_to_bottom_frame(self):
        """Add widgets to the bottom frame."""
        self.bottom_label = customtkinter.CTkLabel(self.bottom_frame, text="Status: Ready", font=("Arial", 18, "italic"))
        self.bottom_label.grid(row=0, column=0, padx=10, pady=5)

        self.word_count_label = customtkinter.CTkLabel(self.bottom_frame, text="0 words", font=("Arial", 18, "italic"))
        self.word_count_label.grid(row=0, column=1, padx=10, pady=5)

        self.progress_bar = customtkinter.CTkProgressBar(self.bottom_frame, height=20, width=600, progress_color="#00A96E")
        self.progress_bar.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.progress_bar.set(0)  # Set the initial value of the progress bar to 0

        self.cancel_button = customtkinter.CTkButton(self.bottom_frame, text="Cancel", font=("Arial", 12), fg_color="#FF0000", command=self.cancel_operation)
        self.cancel_button.grid(row=1, column=1, padx=10, pady=10)

    def change_theme(self, theme):
        """Change the theme of the application."""
        customtkinter.set_appearance_mode(theme)

    def update_word_count(self):
        """Update the word count based on the text in the textbox."""
        text = self.textbox.get("1.0", "end").strip()
        word_count = len(text.split())
        self.word_count_label.configure(text=f"{word_count} words")

    def update_status(self, status_text):
        """Update the status label with the given text."""
        self.status_label.configure(text=f"Status: {status_text}")

    def generate_tts(self):
        """Handle TTS generation logic."""
        text = self.textbox.get("1.0", "end").strip()
        if not text:
            messagebox.showwarning("Warning", "Please enter some text!")
            return

        output_file = filedialog.asksaveasfilename(
            defaultextension=".mp3",
            filetypes=[("MP3 Files", "*.mp3"), ("All Files", "*.*")]
        )
        if not output_file:
            return

        self.generating_status = True  # Start blinking status
        self.blink_status()  # Start the blinking effect
        self.progress_bar.set(0.0)
        self.play_button.configure(state="disabled")  # Disable play button during generation
        self.cancel_button.configure(state="normal")  # Enable cancel button during generation
        self.cancelled = False  # Reset cancellation flag

        # Define a callback to update the progress bar
        def update_progress(progress):
            self.after(0, lambda: self.progress_bar.set(progress))

        # Run the TTS generation in a separate thread
        threading.Thread(target=lambda: asyncio.run(self.async_generate_tts(text, self.selected_voice, output_file, update_progress))).start()

    def blink_status(self):
        """Blink the status label to indicate generating."""
        if self.generating_status:
            current_text = self.status_label.cget("text")
            if current_text.endswith("..."):
                new_text = "Generating"
            else:
                new_text = current_text + "."
            self.status_label.configure(text=new_text)
            self.after(500, self.blink_status)  # Schedule the next update in 500ms

    async def async_generate_tts(self, text, voice, output_file, progress_callback):
        """Run TTS generation asynchronously."""
        try:
            # Define a callback to update the status with the current chunk
            def update_status_with_chunk(status_text):
                self.after(0, lambda: self.update_status(status_text))

            await process_text_to_speech(
                text, 
                voice, 
                output_file, 
                progress_callback, 
                update_status_with_chunk, 
                self.is_cancelled
            )
            if not self.cancelled:
                self.update_status("Completed")
                self.progress_bar.set(1.0)
                self.play_button.configure(state="normal")  # Enable play button after generation
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate TTS: {e}")
            self.update_status("Error")
        finally:
            self.generating_status = False  # Stop blinking status
            self.cancel_button.configure(state="disabled")  # Disable cancel button after generation

    def play_audio(self):
        """Handle playing the generated audio."""
        try:
            play_audio()
            # self.update_status("Playing audio...")  # Remove or comment out this line if status update is not needed
        except Exception as e:
            messagebox.showerror("Error", f"Failed to play audio: {e}")

    def select_voice(self, voice):
        """Handle voice selection logic."""
        self.selected_voice = voice
        self.update_status(f"Voice set to {voice}")

    def cancel_operation(self):
        """Handle cancel operation."""
        self.cancelled = True
        self.update_status("Operation canceled")
        self.progress_bar.set(0)
        self.cancel_button.configure(state="disabled")  # Disable cancel button when operation is canceled

    def is_cancelled(self):
        """Check if the operation has been cancelled."""
        return self.cancelled

def start_gui():
    """Start the GUI application."""
    app = App()
    app.mainloop()
