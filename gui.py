import threading
import customtkinter as ctk
from scraper import YouTubeScraper
import os

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("YouTube Transcript Scraper")
        self.geometry("600x500")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        # Title
        self.label_title = ctk.CTkLabel(self, text="YouTube Transcript Scraper", font=("Roboto", 24, "bold"))
        self.label_title.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Inputs Frame
        self.frame_inputs = ctk.CTkFrame(self)
        self.frame_inputs.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.frame_inputs.grid_columnconfigure(1, weight=1)

        # Channel URL
        self.label_url = ctk.CTkLabel(self.frame_inputs, text="Channel URL:")
        self.label_url.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.entry_url = ctk.CTkEntry(self.frame_inputs, placeholder_text="https://www.youtube.com/@ChannelName")
        self.entry_url.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # Count
        self.label_count = ctk.CTkLabel(self.frame_inputs, text="Video Count:")
        self.label_count.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.entry_count = ctk.CTkEntry(self.frame_inputs, placeholder_text="10")
        self.entry_count.insert(0, "10")
        self.entry_count.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # Sort
        self.label_sort = ctk.CTkLabel(self.frame_inputs, text="Sort By:")
        self.label_sort.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.option_sort = ctk.CTkOptionMenu(self.frame_inputs, values=["Latest", "Popular"])
        self.option_sort.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        # Buttons
        self.btn_start = ctk.CTkButton(self, text="Start Scraping", command=self.start_scraping, height=40, font=("Roboto", 14, "bold"))
        self.btn_start.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.btn_open = ctk.CTkButton(self, text="Open Output Folder", command=self.open_folder, fg_color="transparent", border_width=2)
        self.btn_open.grid(row=3, column=0, padx=20, pady=5, sticky="ew")

        # Log
        self.textbox_log = ctk.CTkTextbox(self, width=500, height=150)
        self.textbox_log.grid(row=4, column=0, padx=20, pady=20, sticky="nsew")
        self.textbox_log.insert("0.0", "Ready to scrape...\n")

        self.scraper = YouTubeScraper()

    def log(self, message):
        self.textbox_log.insert("end", message + "\n")
        self.textbox_log.see("end")

    def start_scraping(self):
        url = self.entry_url.get().strip()
        if not url:
            self.log("Error: Please enter a URL.")
            return

        try:
            count = int(self.entry_count.get())
        except ValueError:
            self.log("Error: Invalid count.")
            return

        sort_mode = "popular" if self.option_sort.get() == "Popular" else "newest"

        self.btn_start.configure(state="disabled", text="Scraping...")
        self.textbox_log.delete("0.0", "end")
        
        # Run in thread to keep UI responsive
        thread = threading.Thread(target=self.run_thread, args=(url, count, sort_mode))
        thread.start()

    def run_thread(self, url, count, sort_mode):
        try:
            self.scraper.run_scrape(url, count, sort_mode, callback=self.log)
            self.log("--------------------------------")
            self.log("COMPLETED SUCCESSFULLY!")
        except Exception as e:
            self.log(f"CRITICAL ERROR: {e}")
        finally:
            self.btn_start.configure(state="normal", text="Start Scraping")

    def open_folder(self):
        path = os.path.join(os.getcwd(), "transcripts")
        if os.path.exists(path):
            os.startfile(path)
        else:
            os.startfile(os.getcwd())

if __name__ == "__main__":
    app = App()
    app.mainloop()
