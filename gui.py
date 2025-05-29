import customtkinter as ctk
from CTkExtendedGraph import CTkExtendedGraph
from tkinter import filedialog
from main import get_links, get_data
import sys
import threading
import os
import csv

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

data = ()


class ConsoleRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        self.text_widget.insert("end", message)
        self.text_widget.see("end")  # Scroll to the end of the text widget

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
            global genre_data
            genre_data = {}
            if os.path.exists("output_genre_data.csv"):
                with open('output_genre_data.csv', 'r', encoding='utf-8') as csvfile:
                    reader = csv.reader(csvfile)
                    next(reader)  # Skip the header row
                    for row in reader:
                        genre = row[0]
                        average_stars = float(row[1])
                        count = int(row[2])
                        genre_data[genre] = (average_stars, count)
            

    threading.Thread(target=task).start()

def scrape_links():
    def task():
        # Call get_links with the number of threads specified
        get_links(num_pages=int(pages.get()) if pages.get().isdigit() and int(pages.get()) > 0 else 1, num_threads=int(threads.get()) if threads.get().isdigit() and int(threads.get()) > 0 else 1)

    threading.Thread(target=task).start()

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Movie Link Scraper")
        self.geometry("800x600")
        self.iconbitmap("crawler.ico")
        
        tabview = ctk.CTkTabview(self, width=800, height=600)
        tabview.pack(expand=True, fill="both")

        # Frames
        tab1 = tabview.add("Scraper")
        button_frame = ctk.CTkFrame(tab1)
        button_frame.pack(side="bottom", pady=10)

        inputs_frame = ctk.CTkFrame(tab1)
        inputs_frame.pack(side='top', anchor='center', pady=20)

        # Buttons
        import_button = ctk.CTkButton(button_frame, text="Import Links", command=import_links)
        scrape_button = ctk.CTkButton(button_frame, text="Scrape Links", command=scrape_links)

        # Label and Entry
        label = ctk.CTkLabel(inputs_frame, text="Number of Threads:")
        label.pack(side="left", padx=5)

        global threads
        threads = ctk.CTkEntry(inputs_frame, width=100)
        threads.pack(side="left", padx=5)
        
        label2 = ctk.CTkLabel(inputs_frame, text="Number of Pages:")
        label2.pack(side="left", padx=5)
        
        global pages
        pages = ctk.CTkEntry(inputs_frame, width=100)
        pages.pack(side="left", padx=5)

        import_button.pack(side="left", padx=5, pady=5)
        scrape_button.pack(side="left", padx=5, pady=5)

        # Text widget for console output
        global text_widget
        text_widget = ctk.CTkTextbox(tab1, width=750, height=400)
        text_widget.pack(pady=10)

        # Redirect console output to the text widget
        sys.stdout = ConsoleRedirector(text_widget)
        tab2 = tabview.add("Visualizer")
        tab2_label = ctk.CTkLabel(tab2, text="This is Tab 2", font=("Arial", 16))
        tab2_label.pack(pady=20)
        graph = CTkExtendedGraph(tab2, "Charged Energy", data, category_labels=("Solar", "Grid"), category_colors=("#FF5733", "#33FFCE"), unit="kWh")
        graph.pack(fill='both', expand=True)
        
        def on_button_click():
            graph.add_new_entry({"Jan": (100, 10)})

            button = ctk.CTkButton(app, text="Test", command=on_button_click)
            button.pack()


# Run the application
app = App()
app.mainloop()