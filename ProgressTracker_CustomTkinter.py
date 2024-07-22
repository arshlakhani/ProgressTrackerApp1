import pandas as pd
import customtkinter as ctk
from tkinter import filedialog, messagebox, BooleanVar
import sqlite3
import time

TrackerPath = 'trackingnew.xlsx'
ProgressTrackerPath = 'progress_tracker.db'
TrackerDf = pd.read_excel(TrackerPath)

steps = [
    {"name": "Application submission in o/o DTCP", "approval": ["RECORD"],
     "sub_steps": ["Application submission in o/o DTCP"]},
    {"name": "Scrutiny of Documents by o/o DTCP", "approval": ["JD", "PA", "ATP", "DTP", "STP"],
     "sub_steps": ["Scrutiny of Documents by o/o DTCP"]},
    {"name": "Letter forwarding circulation of BPs to DTP & STP(Circle), SE-HSVP, Fire officer-ULB, PKL and Observations letter issued",
     "sub_steps": ["Letter forwarding circulation of BPs to DTP & STP(Circle), SE-HSVP, Fire officer-ULB, PKL and Observations letter issued"],
     "approval": ["STP(HQL)"]},
    {"name": "Examination by Concerned Circle - District Town Planner office",
     "sub_steps": ["Examination by Concerned Circle - District Town Planner office", "Compilation of observations"],
     "approval": ["JD", "SD", "PA", "ATP", "DTP"]},
    {"name": "Examination by Concerned Circle - Senior Town Planner office",
     "sub_steps": ["Examination by Concerned Circle - Senior Town Planner office", "Compilation of observations", "Site reports receival"],
     "approval": ["JD", "ATP", "STP"]},
    {"name": "Examination by SE / Executive Engineer - HSVP",
     "sub_steps": ["Examination by SE / Executive Engineer - HSVP", "Compilation of observations", "Site reports receival"],
     "approval": ["JD", "SDM", "HDM", "CHD", "SDE", "CHD", "SDO", "XEN", "SE", "CE", "SE"]},
    {"name": "Examination by Fire Officer, Urban Local Bodies",
     "sub_steps": ["Examination by Fire Officer, Urban Local Bodies", "Compilation of observations", "Site reports receival"],
     "approval": ["ASST.", "SUPDT.", "CONSULTANT", "FIRE OFFICER"]},
    {"name": "Compilation of Reports in o/o DTCP", "sub_steps": ["Compilation of Reports in o/o DTCP"],
     "approval": ["JD", "PA", "ATP", "DTP", "ARCHITECT", "STP", "ARCHITECT", "CTP", "DTP"]},
    {"name": "Fixing of Meeting of BPAC to review the comments / report of all above",
     "sub_steps": ["Fixing of Meeting of BPAC to review the comments / report of all above"], "approval": ["STP"]},
    {"name": "Plan reviewed in BPAC Committee", "sub_steps": ["Plan reviewed in BPAC Committee"],
     "approval": ["o/o DTCP"]},
    {"name": "Observations conveyed", "sub_steps": ["Observations conveyed"]},
    {"name": "Resubmission of Dwgs after compliance", "sub_steps": ["Resubmission of Dwgs after compliance"]},
    {"name": "Circulation of BPs to STP (circle)GGN, SE-HSVP, Fire officer-ULB, Pkl for signatures.",
     "sub_steps": ["Circulation of BPs to STP (circle)GGN, SE-HSVP, Fire officer-ULB, Pkl for signatures."]},
    {"name": "Examination of BPs at Field offices", "sub_steps": ["Examination of BPs at Field offices"]},
    {"name": "Compilation of Reports in o/o DTCP", "sub_steps": ["Compilation of Reports in o/o DTCP"],
     "approval": ["JD"]},
    {"name": "Verification of the Licence / CLU permission / pending dues by the Department",
     "sub_steps": ["Verification of the Licence / CLU permission / pending dues by the Department", "sub_steps"],
     "approval": ["SO", "AO", "CAO"]},
    {"name": "Approved Building Plans & BR-III issued", "sub_steps": ["Approved Building Plans & BR-III issued"],
     "approval": ["JD", "ATP", "DTP", "ARCHITECT", "STP", "CTP"]}
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

# Initialize customtkinter
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("Projects")
root.geometry('400x400')


def showProjectList():
    cursor.execute("SELECT name FROM projectList")
    rows = cursor.fetchall()
    project_names = [row[0] for row in rows]

    window = ctk.CTkToplevel(root)
    window.title("Project List")

    for project_name in project_names:
        newButton = ctk.CTkButton(window, text=project_name, command=lambda name=project_name: openProject(name))
        newButton.pack(pady=5)


def openStepDetails(project_name, step_name, sub_steps, approvals):
    def markCompleted(step, sub_step, completed, submitted_date, completed_date):
        cursor.execute(f'''
        UPDATE progress_{project_name} 
        SET completed = ?, submitted_date = ?, completed_date = ?
        WHERE step = ? AND sub_step = ?
        ''', (completed, submitted_date, completed_date, step, sub_step))
        conn.commit()

    def saveProgress():
        for checkbox, sub_step, submitted_entry, completed_entry, doc_entry in sub_step_vars:
            submitted_date = submitted_entry.get() if submitted_entry.get() else None
            completed_date = completed_entry.get() if completed_entry.get() else None
            document_path = doc_entry.get() if doc_entry.get() else None
            markCompleted(step_name, sub_step, checkbox.get(), submitted_date, completed_date)

        for checkbox, approval, submitted_entry, completed_entry, doc_entry in approval_vars:
            submitted_date = submitted_entry.get() if submitted_entry.get() else None
            completed_date = completed_entry.get() if completed_entry.get() else None
            document_path = doc_entry.get() if doc_entry.get() else None
            markCompleted(step_name, approval, checkbox.get(), submitted_date, completed_date)

        messagebox.showinfo("Info", "Progress Saved")

    window = ctk.CTkToplevel(root)
    window.title(f"Step Details: {step_name}")

    step_frame = ctk.CTkFrame(window)
    step_frame.pack(fill="both", padx=10, pady=10)

    sub_step_vars = []
    for sub_step in sub_steps:
        var = BooleanVar()
        submitted_entry = ctk.CTkEntry(step_frame, placeholder_text="Submitted Date")
        completed_entry = ctk.CTkEntry(step_frame, placeholder_text="Completed Date")
        doc_entry = ctk.CTkEntry(step_frame, placeholder_text="Document Link")

        cursor.execute(f'''
        SELECT completed, submitted_date, completed_date, document_path FROM progress_{project_name} 
        WHERE step = ? AND sub_step = ?
        ''', (step_name, sub_step))
        result = cursor.fetchone()
        if result:
            var.set(result[0])
            if result[1]:
                submitted_entry.insert(0, result[1])
            if result[2]:
                completed_entry.insert(0, result[2])
            if result[3]:
                doc_entry.insert(0, result[3])
        else:
            cursor.execute(f'''
            INSERT INTO progress_{project_name} (step, sub_step, created_time, target_time, actual_time, document_path, completed, completed_time, submitted_date, completed_date) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (step_name, sub_step, time.time(), time.time() + 7.862e+6, None, None, False, None, None, None))
            conn.commit()

        checkbox = ctk.CTkCheckBox(step_frame, text=sub_step, variable=var)
        checkbox.pack(pady=5)
        submitted_entry.pack(pady=5)
        completed_entry.pack(pady=5)
        doc_entry.pack(pady=5)
        sub_step_vars.append((var, sub_step, submitted_entry, completed_entry, doc_entry))

    approval_frame = ctk.CTkFrame(window)
    approval_frame.pack(fill="both", padx=10, pady=10)

    approval_vars = []
    for approval in approvals:
        var = BooleanVar()
        submitted_entry = ctk.CTkEntry(approval_frame, placeholder_text="Submitted Date")
        completed_entry = ctk.CTkEntry(approval_frame, placeholder_text="Completed Date")
        doc_entry = ctk.CTkEntry(approval_frame, placeholder_text="Document Link")

        cursor.execute(f'''
        SELECT completed, submitted_date, completed_date, document_path FROM progress_{project_name} 
        WHERE step = ? AND sub_step = ?
        ''', (step_name, approval))
        result = cursor.fetchone()
        if result:
            var.set(result[0])
            if result[1]:
                submitted_entry.insert(0, result[1])
            if result[2]:
                completed_entry.insert(0, result[2])
            if result[3]:
                doc_entry.insert(0, result[3])
        else:
            cursor.execute(f'''
            INSERT INTO progress_{project_name} (step, sub_step, created_time, target_time, actual_time, document_path, completed, completed_time, submitted_date, completed_date) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (step_name, approval, time.time(), time.time() + 7.862e+6, None, None, False, None, None, None))
            conn.commit()

        checkbox = ctk.CTkCheckBox(approval_frame, text=approval, variable=var)
        checkbox.pack(pady=5)
        submitted_entry.pack(pady=5)
        completed_entry.pack(pady=5)
        doc_entry.pack(pady=5)
        approval_vars.append((var, approval, submitted_entry, completed_entry, doc_entry))

    save_button = ctk.CTkButton(window, text="Save Progress", command=saveProgress)
    save_button.pack(pady=10)


def openProject(project_name):
    window = ctk.CTkToplevel(root)
    window.title(f"Project: {project_name}")

    for step in steps:
        step_button = ctk.CTkButton(window, text=step['name'],
                                    command=lambda step=step: openStepDetails(project_name, step['name'], step['sub_steps'],
                                                                              step['approval']))
        step_button.pack(pady=5, fill="both")

    download_button = ctk.CTkButton(window, text="Download Progress", command=lambda: downloadProgress(project_name))
    download_button.pack(pady=5, fill="both")


def projectTop():
    def addProject(name, desc, topl):
        cursor.execute(f"INSERT INTO projectList (name, desc, created_time, estimated_time) VALUES (?, ?, ?, ?)",
                       (name, desc, time.time(), time.time() + 7.862e+6))
        conn.commit()
        project_name = str(name).replace(" ", "_")
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
            completed_date TEXT
        )
        ''')
        conn.commit()  # Ensure the changes are committed to the database
        projectAdded = ctk.CTkToplevel(topl)
        projectAdded.title("Project Added")
        newLabel = ctk.CTkLabel(projectAdded, text="Project Added")
        newLabel.pack(pady=10)

    window = ctk.CTkToplevel(root)
    window.title("Creating New Project")

    projectName_label = ctk.CTkLabel(window, text="Project Name:")
    projectName_label.pack(pady=5)
    projectName_entry = ctk.CTkEntry(window, placeholder_text="Enter project name")
    projectName_entry.pack(pady=5)

    projectDesc_label = ctk.CTkLabel(window, text="Project Description:")
    projectDesc_label.pack(pady=5)
    projectDesc_entry = ctk.CTkEntry(window, placeholder_text="Enter project description")
    projectDesc_entry.pack(pady=5)

    projectSave_button = ctk.CTkButton(window, text="Save Entries",
                                       command=lambda: addProject(projectName_entry.get(), projectDesc_entry.get(), window))
    projectSave_button.pack(pady=10)


def downloadProgress(project_name):
    cursor.execute(f"SELECT * FROM progress_{project_name}")
    rows = cursor.fetchall()
    progress_df = pd.DataFrame(rows, columns=["ID", "Step", "Sub Step", "Created Time", "Target Time", "Actual Time", "Document Path", "Completed", "Completed Time", "Submitted Date", "Completed Date"])
    progress_df.to_excel(f"{project_name}_progress.xlsx", index=False)
    messagebox.showinfo("Info", f"Progress for {project_name} downloaded as Excel file.")


# Main Window
main_frame = ctk.CTkFrame(root)
main_frame.pack(fill="both", expand=True, padx=10, pady=10)

project_button = ctk.CTkButton(main_frame, text="Add New Project", command=projectTop)
project_button.pack(pady=10)

show_project_button = ctk.CTkButton(main_frame, text="Show Project List", command=showProjectList)
show_project_button.pack(pady=10)

root.mainloop()
