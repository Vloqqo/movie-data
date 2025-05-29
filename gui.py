import tkinter as tk
from tkinter import filedialog
from main import get_links, get_data
import sys
import threading

class ConsoleRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        self.text_widget.insert(tk.END, message)
        self.text_widget.see(tk.END)  # Scroll to the end of the text widget

    def flush(self):
        pass  # Required for compatibility with sys.stdout

def import_links():
    def task():
        file_path = filedialog.askopenfilename(title="Select a file", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            with open(file_path, 'r') as file:
                links = file.readlines()
                links = [link.strip() for link in links if link.strip()]
            print(f"Imported {len(links)} links.")
            # Call get_data with the links
            get_data(links, num_threads=int(threads.get()) if threads.get().isdigit() and int(threads.get()) > 0 else 1)

    threading.Thread(target=task).start()

def scrape_links():
    def task():
        # Call get_links with the number of threads specified
        get_links(num_pages=10, num_threads=int(threads.get()) if threads.get().isdigit() and int(threads.get()) > 0 else 1)

    threading.Thread(target=task).start()

class App(tk.Tk):
    def __init__(self):
        super().__init__()

app = App()
app.title("Movie Link Scraper")
button_frame = tk.Frame(app)
button_frame.pack(side="bottom", pady=10)
inputs_frame = tk.Frame(app)
inputs_frame.pack(side='top', anchor='center', pady=100)
import_button = tk.Button(button_frame, text="Import Links", command=import_links)
scrape_button = tk.Button(button_frame, text="Scrape Links", command=scrape_links)
label = tk.Label(inputs_frame, text="Number of Threads:")
label.pack(side="left")
threads = tk.Entry(inputs_frame)
threads.pack(side="left")
import_button.pack(side="left", padx=5, pady=5)
scrape_button.pack(side="left", padx=5, pady=5)
text_widget = tk.Text(app)
text_widget.pack()

# Redirect console output to the text widget
sys.stdout = ConsoleRedirector(text_widget)

app.mainloop()