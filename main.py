import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import sqlite3

# Load the Excel file to match the headings
#file_path = 'Tracker.xlsx'
#df = pd.read_excel(file_path)

# Updated steps list with sub-steps
steps = [
    {"name": "Application submission in o/o DTCP", "sub_steps": []},
    {"name": "Scrutiny of Documents by o/o DTCP", "sub_steps": []},
    {"name": "Letter forwarding circulation of BPs to DTP & STP(Circle), SE-HSVP, Fire officer-ULB, PKL and Observations letter issued", "sub_steps": []},
    {"name": "Examination by Concerned Circle - District Town Planner office", "sub_steps": ["Compilation of observations"]},
    {"name": "Examination by Concerned Circle - Senior Town Planner office", "sub_steps": ["Compilation of observations", "Site reports receival"]},
    {"name": "Examination by SE / Executive Engineer - HSVP", "sub_steps": ["Compilation of observations", "Site reports receival"]},
    {"name": "Examination by Fire Officer, Urban Local Bodies", "sub_steps": ["Compilation of observations", "Site reports receival"]},
    {"name": "Compilation of Reports in o/o DTCP", "sub_steps": []},
    {"name": "Fixing of Meeting of BPAC to review the comments / report of all above", "sub_steps": []},
    {"name": "Plan reviewed in BPAC Committee", "sub_steps": []},
    {"name": "Observations conveyed", "sub_steps": []},
    {"name": "Resubmission of Dwgs after compliance", "sub_steps": []},
    {"name": "Circulation of BPs to STP (circle)GGN, SE-HSVP, Fire officer-ULB, Pkl for signatures.", "sub_steps": []},
    {"name": "Examination of BPs at Field offices", "sub_steps": []},
    {"name": "Compilation of Reports in o/o DTCP", "sub_steps": []},
    {"name": "Verification of the Licence / CLU permission / pending dues by the Department", "sub_steps": []},
    {"name": "Approved Building Plans & BR-III issued", "sub_steps": []}
]

# Set up SQLite database
conn = sqlite3.connect('progress_tracker.db')
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS progress (
    id INTEGER PRIMARY KEY,
    step TEXT,
    sub_step TEXT,
    target_time TEXT,
    actual_time TEXT,
    document_path TEXT,
    completed BOOLEAN
)
''')
conn.commit()

# Create the main Tkinter window
root = tk.Tk()
root.title("Progress Tracker")

# Function to add entry
def add_entry(step, sub_step, target_time, actual_time, document_path, completed):
    cursor.execute("INSERT INTO progress (step, sub_step, target_time, actual_time, document_path, completed) VALUES (?, ?, ?, ?, ?, ?)",
                   (step, sub_step, target_time, actual_time, document_path, completed))
    conn.commit()

# Function to attach a document
def attach_document():
    file_path = filedialog.askopenfilename()
    return file_path

# Function to create a new window for each step
def open_step_window(step):
    window = tk.Toplevel(root)
    window.title(step["name"])

    sub_steps_status = {}

    def update_sub_step(sub_step):
        sub_steps_status[sub_step] = sub_steps_status.get(sub_step, False)
        sub_steps_status[sub_step] = not sub_steps_status[sub_step]

    def save_entries():
        for sub_step, completed in sub_steps_status.items():
            add_entry(step["name"], sub_step, target_time_entry.get(), actual_time_entry.get(), document_label.cget("text").replace("Document: ", ""), completed)
        messagebox.showinfo("Entries Saved", f"Progress entries for '{step['name']}' saved successfully!")

    target_time_label = tk.Label(window, text="Target Time:")
    target_time_label.pack()
    target_time_entry = tk.Entry(window)
    target_time_entry.pack()

    actual_time_label = tk.Label(window, text="Actual Time:")
    actual_time_label.pack()
    actual_time_entry = tk.Entry(window)
    actual_time_entry.pack()

    document_label = tk.Label(window, text="Document:")
    document_label.pack()
    attach_button = tk.Button(window, text="Attach Document", command=lambda: document_label.config(text=f"Document: {attach_document()}"))
    attach_button.pack()

    for sub_step in step["sub_steps"]:
        var = tk.BooleanVar()
        sub_step_checkbox = tk.Checkbutton(window, text=sub_step, variable=var, command=lambda sub_step=sub_step: update_sub_step(sub_step))
        sub_step_checkbox.pack()
        sub_steps_status[sub_step] = var

    save_button = tk.Button(window, text="Save Entries", command=save_entries)
    save_button.pack()

    if not step["sub_steps"]:
        sub_steps_status["Main Step"] = tk.BooleanVar()
        sub_step_checkbox = tk.Checkbutton(window, text="Main Step", variable=sub_steps_status["Main Step"], command=lambda: update_sub_step("Main Step"))
        sub_step_checkbox.pack()

# Function to export data to Excel
def export_to_excel():
    export_df = pd.read_sql_query("SELECT * FROM progress", conn)
    export_df.to_excel('exported_progress.xlsx', index=False)
    messagebox.showinfo("Export", "Data exported successfully!")

# Create buttons for each step
for step in steps:
    button = tk.Button(root, text=step["name"], command=lambda step=step: open_step_window(step))
    button.pack()

export_button = tk.Button(root, text="Export to Excel", command=export_to_excel)
export_button.pack()

root.mainloop()
