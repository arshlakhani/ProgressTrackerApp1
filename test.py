import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import sqlite3
from datetime import datetime
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Border, Side

TrackerPath = 'trackingnew.xlsx'
ProgressTrackerPath = 'progress_tracker.db'
TrackerDf = pd.read_excel(TrackerPath)

steps = [
    {"name": "Application submission in o/o DTCP", "approval": ["RECORD"],
     "sub_steps": ["Application submission in o/o DTCP"]},
    {"name": "Scrutiny of Documents by o/o DTCP", "approval": ["JD", "PA", "ATP", "DTP", "STP"],
     "sub_steps": ["Scrutiny of Documents by o/o DTCP"]},
    {
        "name": "Letter forwarding circulation of BPs to DTP & STP(Circle), SE-HSVP, Fire officer-ULB, PKL and Observations letter issued",
        "approval": ["STP(HQ)"], "sub_steps": [
        "Letter forwarding circulation of BPs to DTP & STP(Circle), SE-HSVP, Fire officer-ULB, PKL and Observations letter issued"]},
    {"name": "Examination by Concerned Circle - District Town Planner office", "approval": ["JD", "SD", "PA", "ATP"],
     "sub_steps": ["Examination by Concerned Circle - District Town Planner office"]},
    {"name": "Compilation of observations", "approval": ["DTP"], "sub_steps": ["Compilation of observations"]},
    {"name": "Examination by Concerned Circle - Senior Town Planner office", "approval": ["JD", "ATP"],
     "sub_steps": ["Examination by Concerned Circle - Senior Town Planner office"]},
    {"name": "Compilation of observations1 ", "approval": ["STP"], "sub_steps": ["Compilation of observations"]},
    {"name": "Site reports receival 3", "approval": [""], "sub_steps": ["Site reports receival"]},
    {"name": "Examination by SE / Executive Engineer - HSVP",
     "approval": ["JD", "SDM", "HDM", "CHD", "SDE", "SDO", "XEN", "SE", "CE"],
     "sub_steps": ["Examination by SE / Executive Engineer - HSVP"]},
    {"name": "Compilation of observations2", "approval": ["SE"], "sub_steps": ["Compilation of observations"]},
    {"name": "Site reports receival 2", "approval": [""], "sub_steps": ["Site reports receival"]},
    {"name": "Examination by Fire Officer, Urban Local Bodies",
     "approval": ["ASST.", "SUPDT.", "CONSULTANT", "FIRE OFFICER"],
     "sub_steps": ["Examination by Fire Officer, Urban Local Bodies"]},
    {"name": "Compilation of observations3", "approval": ["FIRE OFFICER"],
     "sub_steps": ["Compilation of observations"]},
    {"name": "Site reports receival 1", "approval": [""], "sub_steps": ["Site reports receival"]},
    {"name": "Compilation of Reports in o/o DTCP",
     "approval": ["JD", "PA", "ATP", "DTP", "ARCHITECT", "STP", "ARCHITECT", "CTP", "DTP "],
     "sub_steps": ["Compilation of Reports in o/o DTCP"]},
    {"name": "Fixing of Meeting of BPAC to review the comments / report of all above", "approval": ["STP"],
     "sub_steps": ["Fixing of Meeting of BPAC to review the comments / report of all above"]},
    {"name": "Plan reviewed in BPAC Committee", "approval": ["o/o DTCP"],
     "sub_steps": ["Plan reviewed in BPAC Committee"]},
    {"name": "Observations conveyed", "approval": [""], "sub_steps": ["Observations conveyed"]},
    {"name": "Resubmission of Dwgs after compliance", "approval": [""],
     "sub_steps": ["Resubmission of Dwgs after compliance"]},
    {"name": "Circulation of BPs to STP (circle)GGN, SE-HSVP, Fire officer-ULB, Pkl for signatures.", "approval": [""],
     "sub_steps": ["Circulation of BPs to STP (circle)GGN, SE-HSVP, Fire officer-ULB, Pkl for signatures."]},
    {"name": "Examination of BPs at Field offices", "approval": [""],
     "sub_steps": ["Examination of BPs at Field offices"]},
    {"name": "Compilation of Reports in o/o DTCP 1", "approval": ["JD"],
     "sub_steps": ["Compilation of Reports in o/o DTCP"]},
    {"name": "Verification of the Licence / CLU permission / pending dues by the Department",
     "approval": ["SO", "AO", "CAO"],
     "sub_steps": ["Verification of the Licence / CLU permission / pending dues by the Department"]},
    {"name": "Approved Building Plans & BR-III issued", "approval": ["JD", "ATP", "DTP", "ARCHITECT", "STP", "CTP"],
     "sub_steps": ["Approved Building Plans & BR-III issued"]}
]

conn = sqlite3.connect(ProgressTrackerPath)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS projectList (
    id INTEGER PRIMARY KEY,
    name TEXT,
    desc TEXT,
    created_time TEXT,
    estimated_time TEXT
)
''')
conn.commit()


def create_progress_table(project_name):
    cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS progress_{project_name} (
        id INTEGER PRIMARY KEY,
        step TEXT,
        sub_step TEXT,
        created_time TEXT,
        target_time TEXT,
        actual_time TEXT,
        document_path TEXT,
        completed BOOLEAN,
        completed_time TEXT,
        submitted_date TEXT,
        completed_date TEXT,
        approval TEXT
    )
    ''')
    conn.commit()


def add_project():
    def submit():
        project_name = name_entry.get()
        desc = desc_entry.get()
        created_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        estimated_time = estimate_entry.get()

        if project_name and desc and estimated_time:
            cursor.execute("INSERT INTO projectList (name, desc, created_time, estimated_time) VALUES (?, ?, ?, ?)",
                           (project_name, desc, created_time, estimated_time))
            conn.commit()
            create_progress_table(project_name)
            messagebox.showinfo("Success", "Project added successfully!")
            add_project_window.destroy()
        else:
            messagebox.showwarning("Warning", "All fields are required")

    add_project_window = tk.Toplevel(root)
    add_project_window.title("Add New Project")

    tk.Label(add_project_window, text="Project Name:").pack()
    name_entry = tk.Entry(add_project_window)
    name_entry.pack()

    tk.Label(add_project_window, text="Description:").pack()
    desc_entry = tk.Entry(add_project_window)
    desc_entry.pack()

    tk.Label(add_project_window, text="Estimated Time:").pack()
    estimate_entry = tk.Entry(add_project_window)
    estimate_entry.pack()

    tk.Button(add_project_window, text="Submit", command=submit).pack()


def showProjectList():
    cursor.execute("SELECT name FROM projectList")
    rows = cursor.fetchall()
    project_names = [row[0] for row in rows]

    window = tk.Toplevel(root)
    window.title("Project List")

    for project_name in project_names:
        newButton = tk.Button(window, text=project_name, command=lambda name=project_name: openProject(name))
        newButton.pack()


def uploadDocument(approval_name, step_name, project_name):
    file_path = filedialog.askopenfilename()
    if file_path:
        cursor.execute(f'''
        UPDATE progress_{project_name} 
        SET document_path = ?
        WHERE step = ? AND approval = ?
        ''', (file_path, step_name, approval_name))
        conn.commit()
        messagebox.showinfo("Info", "Document uploaded successfully!")


def openStepDetails(project_name, step_name, sub_steps, approvals):
    def markCompleted(approval, completed, submitted_date, completed_date):
        cursor.execute(f'''
        UPDATE progress_{project_name} 
        SET completed = ?, submitted_date = ?, completed_date = ?
        WHERE step = ? AND approval = ?
        ''', (completed, submitted_date, completed_date, step_name, approval))
        conn.commit()

    def saveProgress():
        for checkbox, approval, submitted_entry, completed_entry in approval_vars:
            submitted_date = submitted_entry.get() if submitted_entry.get() else None
            completed_date = completed_entry.get() if completed_entry.get() else None
            markCompleted(approval, checkbox.get(), submitted_date, completed_date)

        messagebox.showinfo("Info", "Progress Saved")

    window = tk.Toplevel(root)
    window.title(f"Step Details: {step_name}")

    step_frame = tk.LabelFrame(window, text="Sub-Steps")
    step_frame.pack(fill="both")

    for sub_step in sub_steps:
        var = tk.BooleanVar()
        checkbox = tk.Checkbutton(step_frame, text=sub_step, variable=var)
        checkbox.pack()

    approval_frame = tk.LabelFrame(window, text="Approvals")
    approval_frame.pack(fill="both")

    approval_vars = []

    for approval in approvals:
        var = tk.BooleanVar()
        submitted_entry = tk.Entry(approval_frame, width=20)
        completed_entry = tk.Entry(approval_frame, width=20)

        cursor.execute(f'''
        INSERT INTO progress_{project_name} (step, sub_step, created_time, target_time, actual_time, document_path, completed, completed_time, submitted_date, completed_date, approval)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(step, approval) DO UPDATE SET
        created_time = excluded.created_time,
        target_time = excluded.target_time,
        actual_time = excluded.actual_time,
        document_path = excluded.document_path,
        completed = excluded.completed,
        completed_time = excluded.completed_time,
        submitted_date = excluded.submitted_date,
        completed_date = excluded.completed_date
        ''', (step_name, sub_step, datetime.now(), None, None, None, False, None, None, None, approval))
        conn.commit()

        row = tk.Frame(approval_frame)
        row.pack(fill="x")
        tk.Checkbutton(row, text=approval, variable=var).pack(side="left")
        submitted_label = tk.Label(row, text="Submitted Date:")
        submitted_label.pack(side="left")
        submitted_entry.pack(side="left")
        completed_label = tk.Label(row, text="Completed Date:")
        completed_label.pack(side="left")
        completed_entry.pack(side="left")

        upload_button = tk.Button(row, text="Upload Document",
                                  command=lambda name=approval: uploadDocument(name, step_name, project_name))
        upload_button.pack(side="left")

        approval_vars.append((var, approval, submitted_entry, completed_entry))

    save_button = tk.Button(window, text="Save Progress", command=saveProgress)
    save_button.pack()


def openProject(project_name):
    cursor.execute(f'SELECT DISTINCT step FROM progress_{project_name}')
    steps = cursor.fetchall()

    window = tk.Toplevel(root)
    window.title(f"Project: {project_name}")

    for step in steps:
        step_name = step[0]
        cursor.execute(f'SELECT DISTINCT sub_step, approval FROM progress_{project_name} WHERE step = ?', (step_name,))
        rows = cursor.fetchall()

        for row in rows:
            sub_step = row[0]
            approvals = row[1].split(",") if row[1] else []

            button = tk.Button(window, text=f"Step: {step_name} | Sub-Step: {sub_step}",
                               command=lambda name=step_name, sub=sub_step: openStepDetails(project_name, name, sub,
                                                                                            approvals))
            button.pack()


root = tk.Tk()
root.title("Progress Tracker")

show_button = tk.Button(root, text="Show Projects", command=showProjectList)
show_button.pack()

add_project_button = tk.Button(root, text="Add Project", command=add_project)
add_project_button.pack()

root.mainloop()
