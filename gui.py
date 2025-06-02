import customtkinter as ctk
import numpy as np
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

        # Scrollable frame for graphs
        self.scrollable_frame = ctk.CTkScrollableFrame(self.tab2, width=780, height=580)
        self.scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Initialize the graphs
        self.init_graphs()

        # Buttons
        self.import_button = ctk.CTkButton(button_frame, text="Import Links", command=self.import_links)
        self.scrape_button = ctk.CTkButton(button_frame, text="Scrape Links", command=self.scrape_links)

        # Label and Entry
        label = ctk.CTkLabel(inputs_frame, text="Number of Threads:")
        label.pack(side="left", padx=5)

        self.threads = ctk.CTkEntry(inputs_frame, width=100)  # Changed to self.threads
        self.threads.pack(side="left", padx=5)

        label2 = ctk.CTkLabel(inputs_frame, text="Number of Pages:")
        label2.pack(side="left", padx=5)

        self.pages = ctk.CTkEntry(inputs_frame, width=100)  # Changed to self.pages
        self.pages.pack(side="left", padx=5)

        self.import_button.pack(side="left", padx=5, pady=5)
        self.scrape_button.pack(side="left", padx=5, pady=5)

        # Text widget for console output
        self.text_widget = ctk.CTkTextbox(self.tab1, width=750, height=400)
        self.text_widget.pack(pady=10)

        # Redirect console output to the text widget
        sys.stdout = ConsoleRedirector(self.text_widget)

    def init_graphs(self):
        # Create the first graph using Matplotlib
        self.create_chart(
            data={},
            title="Movie Ratings by Genre",
            category_labels=("Average Rating", ""),
            category_colors=("#FF5733", "#FFB533"),
            unit="★",
            parent=self.scrollable_frame
        )

        # Create the second graph using Matplotlib
        self.create_chart(
            data={},
            title="Average Stars by Movie Name Length",
            category_labels=("Average Stars", ""),
            category_colors=("#33FF57", "#33FFB5"),
            unit="★",
            parent=self.scrollable_frame
        )

    def import_links(self):
        def task():
            file_path = filedialog.askopenfilename(title="Select a file", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
            if file_path:
                with open(file_path, 'r') as file:
                    links = file.readlines()
                    links = [link.strip() for link in links if link.strip()]
                print(f"Imported {len(links)} links.")
                # Call get_data with the links
                get_data(
                    links,
                    num_threads=int(self.threads.get()) if self.threads.get().isdigit() and int(self.threads.get()) > 0 else 1
                )
                # Update the graph after data processing
                _app.update_graph_with_data()

        threading.Thread(target=task).start()

    def scrape_links(self):
        def task():
            # Call get_links with the number of threads and pages specified
            get_links(
                num_pages=int(self.pages.get()) if self.pages.get().isdigit() and int(self.pages.get()) > 0 else 1,
                num_threads=int(self.threads.get()) if self.threads.get().isdigit() and int(self.threads.get()) > 0 else 1
            )

        threading.Thread(target=task).start()

    def create_chart(self, data, title, category_labels, category_colors, unit, parent):
        """
        Creates the stacked bar chart using Matplotlib and embeds it in CustomTkinter.
        """
        # Create Matplotlib figure
        figure, axis = plt.subplots(figsize=(8, 6), facecolor='none')

        # Prepare data for plotting
        categories = list(data.keys())
        category1_values = np.array([data[category][0] for category in categories]) if categories else []
        category2_values = np.array([data[category][1] for category in categories]) if categories else []

        bar_width = 0.5
        index_positions = np.arange(len(categories))

        # Draw bars for the two categories
        axis.bar(index_positions, category1_values, bar_width, color=category_colors[0], label=category_labels[0])
        axis.bar(index_positions, category2_values, bar_width, color=category_colors[1], bottom=category1_values,
                 label=category_labels[1])

        # Set x-axis ticks and labels
        axis.set_xticks(index_positions)
        axis.set_xticklabels(categories, fontsize=10, color='white')

        # Set y-axis limits and ticks
        axis.set_ylim(0, 5)  # Set y-axis limits from 0 to 5
        yticks = np.arange(0, 5.1, 0.5)  # Create ticks from 0 to 5 with 0.5 intervals
        axis.set_yticks(yticks)
        axis.set_yticklabels([f"{tick:.1f} {unit}" for tick in yticks], fontsize=10, color='white')

        axis.set_title(title, fontsize=12, color='white')

        # Set background color for dark mode
        axis.set_facecolor('#0A0A0A')  # Dark gray background for the graph
        figure.patch.set_facecolor('#0A0A0A')  # Dark gray background for the figure

        # Add legend
        legend = axis.legend(facecolor='#0A0A0A', edgecolor='white', fontsize=10)
        for text in legend.get_texts():
            text.set_color("white")

        # Draw grid lines for better readability
        axis.grid(True, linestyle='--', alpha=0.3, color='white')

        # Embed Matplotlib figure into CustomTkinter
        canvas = FigureCanvasTkAgg(figure, master=parent)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill='both', expand=True, pady=10)
        
    def update_graph_with_data(self):
        def task():
            # Clear the scrollable frame to remove old graphs
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()

            # Example: Update the first graph (Movie Ratings by Genre)
            if os.path.exists("output_genre_data.csv"):
                data = {}
                with open('output_genre_data.csv', 'r', encoding='utf-8') as csvfile:
                    reader = csv.reader(csvfile)
                    next(reader)  # Skip header
                    for row in reader:
                        genre = row[0]
                        avg_stars = float(row[1])
                        data[genre] = (avg_stars, 0)  # Add second value as 0

                # Schedule the graph creation on the main thread
                self.after(0, lambda: self.create_chart(
                    data=data,
                    title="Movie Ratings by Genre",
                    category_labels=("Average Rating", ""),
                    category_colors=("#FF5733", "#FFB533"),
                    unit="★",
                    parent=self.scrollable_frame
                ))

            # Example: Update the second graph (Average Stars by Movie Name Length)
            if os.path.exists("name_length_to_average_stars.csv"):
                data = {}
                with open('name_length_to_average_stars.csv', 'r', encoding='utf-8') as csvfile:
                    reader = csv.reader(csvfile)
                    next(reader)  # Skip header
                    for row in reader:
                        name_length = int(row[0])
                        avg_stars = float(row[1])
                        data[name_length] = (avg_stars, 0)  # Add second value as 0

                # Schedule the graph creation on the main thread
                self.after(0, lambda: self.create_chart(
                    data=data,
                    title="Average Stars by Movie Name Length",
                    category_labels=("Average Stars", ""),
                    category_colors=("#33FF57", "#33FFB5"),
                    unit="★",
                    parent=self.scrollable_frame
                ))

    # Run the task in a separate thread to avoid blocking the GUI
        threading.Thread(target=task).start()


class ConsoleRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        self.text_widget.insert("end", message)
        self.text_widget.see("end")  # Scroll to the end of the text widget

    def flush(self):
        pass  # Required for compatibility with sys.stdout


# Run the application
_app = App()
_app.mainloop()