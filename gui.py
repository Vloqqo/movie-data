import tkinter as tk
from tkinter import filedialog
from main import get_links, get_data, all_links
def import_links():
    file_path = filedialog.askopenfilename(title="Select a file", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file_path:
        with open(file_path, 'r') as file:
            links = file.readlines()
            links = [link.strip() for link in links if link.strip()]
        get_data(links)
class App(tk.Tk):
   def __init__(self):
      super().__init__()

app = App()
import_button = tk.Button(app, text="Import Links", command=import_links)
scrape_button = tk.Button(app, text="Scrape Links", command=get_links)
entry = tk.Entry(app)
entry.pack()
import_button.pack(pady=100)
scrape_button.pack(pady=100)
app.mainloop()