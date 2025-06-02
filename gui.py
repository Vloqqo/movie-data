import customtkinter as ctk
import numpy as np
from CTkExtendedGraph import CTkExtendedGraph
from tkinter import filedialog

from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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
            # Update the graph after data processing
            _app.update_graph_with_data()  # Use _app instead of app

    threading.Thread(target=task).start()


def scrape_links():
    def task():
        # Call get_links with the number of threads specified
        get_links(num_pages=int(pages.get()) if pages.get().isdigit() and int(pages.get()) > 0 else 1, num_threads=int(threads.get()) if threads.get().isdigit() and int(threads.get()) > 0 else 1)

    threading.Thread(target=task).start()


def create_chart(self):
    """
    Creates the stacked bar chart using Matplotlib.
    """
    # Create Matplotlib figure
    figure, axis = plt.subplots(figsize=(self.width / 100, self.height / 100), facecolor='none')

    # Prepare data for plotting
    months = list(self.data.keys())
    category1_values = np.array([self.data[month][0] for month in months])
    category2_values = np.array([self.data[month][1] for month in months])

    bar_width = 0.5
    index_positions = np.arange(len(months))

    # Draw bars for the two categories
    axis.bar(index_positions, category1_values, bar_width, color=self.category_colors[0], label=self.category_labels[0])
    axis.bar(index_positions, category2_values, bar_width, color=self.category_colors[1], bottom=category1_values,
             label=self.category_labels[1])

    # Set x-axis ticks and labels
    axis.set_xticks(index_positions)
    axis.set_xticklabels(months, fontsize=10, color='white')

    # Set y-axis limits and ticks
    axis.set_ylim(0, 5)  # Set y-axis limits from 0 to 5
    yticks = np.arange(0, 5.1, 0.5)  # Create ticks from 0 to 5 with 0.5 intervals
    axis.set_yticks(yticks)
    axis.set_yticklabels([f"{tick:.1f} {self.unit}" for tick in yticks], fontsize=10, color='white')

    axis.set_title(self.title, fontsize=12, color='white')

    # Set background color
    axis.set_facecolor('#0A0A0A')
    figure.patch.set_facecolor('#0A0A0A')

    # Add legend
    legend = axis.legend(facecolor='#0A0A0A', edgecolor='white', fontsize=10)
    for text in legend.get_texts():
        text.set_color("white")

    # Draw grid lines for better readability
    axis.grid(True, linestyle='--', alpha=0.3)

    # If there is an existing canvas, remove it
    if self.canvas:
        self.canvas.get_tk_widget().destroy()

    # Embed Matplotlib figure into CustomTkinter
    self.canvas = FigureCanvasTkAgg(figure, master=self)
    self.canvas_widget = self.canvas.get_tk_widget()
    self.canvas_widget.pack(fill='both', expand=True)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Movie Link Scraper")
        self.geometry("800x600")
        self.iconbitmap("crawler.ico")

        self.tabview = ctk.CTkTabview(self, width=800, height=600)
        self.tabview.pack(expand=True, fill="both")

        # Frames
        self.tab1 = self.tabview.add("Scraper")
        self.tab2 = self.tabview.add("Visualizer")

        button_frame = ctk.CTkFrame(self.tab1)
        button_frame.pack(side="bottom", pady=10)

        inputs_frame = ctk.CTkFrame(self.tab1)
        inputs_frame.pack(side='top', anchor='center', pady=20)

        # Initialize the graph
        self.init_graph()

        tabview = ctk.CTkTabview(self, width=800, height=600)
        tabview.pack(expand=True, fill="both")


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
        text_widget = ctk.CTkTextbox(self.tab1, width=750, height=400)
        text_widget.pack(pady=10)

        # Redirect console output to the text widget
        sys.stdout = ConsoleRedirector(text_widget)
        tab2 = tabview.add("Visualizer")
        tab2_label = ctk.CTkLabel(tab2, text="This is Tab 2", font=("Arial", 16))
        tab2_label.pack(pady=20)

    def init_graph(self):
        # Initialize with empty data
        empty_data = {}  # Empty dictionary for initial state
        self.graph = CTkExtendedGraph(
            master=self.tab2,
            title="Movie Ratings by Genre",
            data=empty_data,
            category_labels=("Average Rating", ""),  # Add a second empty category
            category_colors=("#FF5733", "#FFB533"),  # Add a second color
            unit="★"
        )
        self.graph.pack(fill='both', expand=True)

    def update_graph_with_data(self):
        if os.path.exists("output_genre_data.csv"):
            data = {}
            with open('output_genre_data.csv', 'r', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  # Skip header
                for row in reader:
                    genre = row[0]
                    avg_stars = float(row[1])
                    data[genre] = (avg_stars, 0)  # Add second value as 0

            # Create a new graph instance with the data
            if hasattr(self, 'graph'):
                self.graph.destroy()  # Remove old graph

            self.graph = CTkExtendedGraph(
                master=self.tab2,
                title="Movie Ratings by Genre",
                data=data,
                category_labels=("Average Rating", ""),  # Add a second empty category
                category_colors=("#FF5733", "#FFB533"),  # Add a second color
                unit="★"
            )
            self.graph.pack(fill='both', expand=True)


# Run the application
_app = App()  # Store the instance in _app
_app.mainloop()