import customtkinter as ctk
import numpy as np
from tkinter import filedialog
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import defaultdict
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

        self.scrollable_frame = ctk.CTkScrollableFrame(self.tab2, width=780, height=580)
        self.scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # starts up the graphs
        self.init_graphs()

        self.import_button = ctk.CTkButton(button_frame, text="Import Links", command=self.import_links)
        self.scrape_button = ctk.CTkButton(button_frame, text="Scrape Links", command=self.scrape_links)

        label = ctk.CTkLabel(inputs_frame, text="Number of Threads:")
        label.pack(side="left", padx=5)

        self.threads = ctk.CTkEntry(inputs_frame, width=100)
        self.threads.pack(side="left", padx=5)

        label2 = ctk.CTkLabel(inputs_frame, text="Number of Pages:")
        label2.pack(side="left", padx=5)

        self.pages = ctk.CTkEntry(inputs_frame, width=100)
        self.pages.pack(side="left", padx=5)

        self.import_button.pack(side="left", padx=5, pady=5)
        self.scrape_button.pack(side="left", padx=5, pady=5)

        self.text_widget = ctk.CTkTextbox(self.tab1, width=750, height=400)
        self.text_widget.pack(pady=10)

        # console output will show up in this text widget
        sys.stdout = ConsoleRedirector(self.text_widget)

    def update_graph_with_data(self):
        def task():
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()

            if os.path.exists("output_genre_data.csv"):
                data = {}
                with open('output_genre_data.csv', 'r', encoding='utf-8') as csvfile:
                    reader = csv.reader(csvfile)
                    next(reader)  # Skip header
                    for row in reader:
                        genre = row[0]
                        avg_stars = float(row[1])
                        data[genre] = (avg_stars, 0)

                self.after(0, lambda: self.create_chart(
                    data=data,
                    title="Movie Ratings by Genre",
                    category_labels=("Average Rating", ""),
                    category_colors=("#FF5733", "#FFB533"),
                    unit="★",
                    parent=self.scrollable_frame
                ))

            if os.path.exists("name_length_to_average_stars.csv"):
                data = {}
                with open('name_length_to_average_stars.csv', 'r', encoding='utf-8') as csvfile:
                    reader = csv.reader(csvfile)
                    next(reader)  # Skip header
                    for row in reader:
                        name_length = int(row[0])
                        avg_stars = float(row[1])
                        data[name_length] = (avg_stars, 0)

                self.after(0, lambda: self.create_chart(
                    data=data,
                    title="Average Stars by Movie Name Length",
                    category_labels=("Average Stars", ""),
                    category_colors=("#33FF57", "#33FFB5"),
                    unit="★",
                    parent=self.scrollable_frame
                ))

            if os.path.exists("genre_distribution.csv"):
                # Create a nested dictionary to store data by year and genre
                data_by_year_genre = defaultdict(lambda: defaultdict(float))
                genres = set()

                # Read and organize the data
                with open('genre_distribution.csv', 'r', encoding='utf-8') as csvfile:
                    reader = csv.reader(csvfile)
                    next(reader)  # Skip header
                    for row in reader:
                        year = row[0]
                        genre = row[1]
                        percentage = float(row[2])
                        data_by_year_genre[year][genre] = percentage
                        genres.add(genre)

                self.after(0, lambda: self.create_genre_distribution_chart(
                    data=data_by_year_genre,
                    genres=list(genres),
                    title="Genre Distribution Over Time",
                    parent=self.scrollable_frame
                ))

        threading.Thread(target=task).start()

    def create_genre_distribution_chart(self, data, genres, title, parent):
        figure, axis = plt.subplots(figsize=(10, 6), facecolor='none')

        # Check if we have any data to plot
        if not data or not genres:
            axis.text(0.5, 0.5, 'No data available',
                      horizontalalignment='center',
                      verticalalignment='center',
                      color='white',
                      transform=axis.transAxes)
        else:
            years = sorted(data.keys())

            # Create color map for genres
            colors = plt.cm.rainbow(np.linspace(0, 1, len(genres)))

            # Create a dictionary to store point coordinates and their counts
            point_counts = defaultdict(int)

            # Plot each genre as a separate line
            for genre, color in zip(sorted(genres), colors):
                # Collect points for current genre
                points = []
                for year in years:
                    percentage = data[year].get(genre, 0)
                    point_counts[(year, percentage)] += 1
                    points.append((year, percentage))

                # Plot lines first
                x_coords = [p[0] for p in points]
                y_coords = [p[1] for p in points]
                axis.plot(x_coords, y_coords, '-', color=color, alpha=0.3, zorder=1)

                # Plot points with size based on overlap count
                for x, y in points:
                    count = point_counts[(x, y)]
                    size = 100 + (count * 50)
                    axis.scatter(x, y, s=size, color=color, alpha=0.6,
                                 label=genre if (x, y) == points[0] else "",
                                 zorder=2)

                    if count > 1:
                        axis.text(x, y, str(count),
                                  horizontalalignment='center',
                                  verticalalignment='center',
                                  color='white',
                                  fontweight='bold',
                                  fontsize=10,
                                  zorder=3)

        axis.set_xlabel('Year', color='white')
        axis.set_ylabel('Percentage of Movies', color='white')
        axis.set_title(title, fontsize=12, color='white')

        plt.xticks(rotation=45, ha='right', color='white')
        plt.yticks(color='white')
        axis.set_ylim(0, 100)

        # Customize appearance
        axis.set_facecolor('#0A0A0A')
        figure.patch.set_facecolor('#0A0A0A')
        axis.tick_params(colors='white')

        for spine in axis.spines.values():
            spine.set_color('white')
            spine.set_visible(True)

        axis.grid(True, color='gray', alpha=0.2)
        legend = axis.legend(bbox_to_anchor=(1.05, 1), loc='upper left',
                             facecolor='#0A0A0A', edgecolor='white')
        for text in legend.get_texts():
            text.set_color('white')
        plt.tight_layout()

        canvas = FigureCanvasTkAgg(figure, master=parent)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill='both', expand=True, pady=10)

    def init_graphs(self):
        # creates the graphs that will be in gui
        self.create_chart(
            data={},
            title="Movie Ratings by Genre",
            category_labels=("Average Rating", ""),
            category_colors=("#FF5733", "#FFB533"),
            unit="★",
            parent=self.scrollable_frame
        )

        self.create_chart(
            data={},
            title="Average Stars by Movie Name Length",
            category_labels=("Average Stars", ""),
            category_colors=("#33FF57", "#33FFB5"),
            unit="★",
            parent=self.scrollable_frame
        )
        self.create_genre_distribution_chart(
            data={},
            genres=[],
            title="Genre Distribution Over Time",
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
                get_data(
                    links,
                    num_threads=int(self.threads.get()) if self.threads.get().isdigit() and int(self.threads.get()) > 0 else 1
                )
                _app.update_graph_with_data()

        threading.Thread(target=task).start()

    def scrape_links(self):
        def task():
            get_links(
                num_pages=int(self.pages.get()) if self.pages.get().isdigit() and int(self.pages.get()) > 0 else 1,
                num_threads=int(self.threads.get()) if self.threads.get().isdigit() and int(self.threads.get()) > 0 else 1
            )

        threading.Thread(target=task).start()

    def create_chart(self, data, title, category_labels, category_colors, unit, parent):
        figure, axis = plt.subplots(figsize=(8, 6), facecolor='none')
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
        yticks = np.arange(0, 5.1, 0.5)
        axis.set_yticks(yticks)
        axis.set_yticklabels([f"{tick:.1f} {unit}" for tick in yticks], fontsize=10, color='white')

        axis.set_title(title, fontsize=12, color='white')

        axis.set_facecolor('#0A0A0A')  # Dark gray background for the graph
        figure.patch.set_facecolor('#0A0A0A')  # Dark gray background for the figure

        legend = axis.legend(facecolor='#0A0A0A', edgecolor='white', fontsize=10)
        for text in legend.get_texts():
            text.set_color("white")

        # embedding matplotlib chart into customtkinter
        canvas = FigureCanvasTkAgg(figure, master=parent)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill='both', expand=True, pady=10)



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