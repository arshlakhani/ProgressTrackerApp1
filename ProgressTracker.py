import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import sqlite3
import time

TrackerPath = 'Tracker.xlsx'
ProgressTrackerPath = 'progress_tracker.db'
TrackerDf = pd.read_excel(TrackerPath)

steps = [
    {"name": "Application submission in o/o DTCP", "approval": ["RECORD"], "sub_steps": ["Application submission in o/o DTCP"]},
    {"name": "Scrutiny of Documents by o/o DTCP", "approval": ["JD","PA","ATP","DTP","STP"], "sub_steps": ["Scrutiny of Documents by o/o DTCP"]},
    {"name": "Letter forwarding circulation of BPs to DTP & STP(Circle), SE-HSVP, Fire officer-ULB, PKL and Observations letter issued", "sub_steps": ["Letter forwarding circulation of BPs to DTP & STP(Circle), SE-HSVP, Fire officer-ULB, PKL and Observations letter issued"], "approval": ["STP(HQL)"]},
    {"name": "Examination by Concerned Circle - District Town Planner office", "sub_steps": ["Examination by Concerned Circle - District Town Planner office","Compilation of observations"], "approval": ["JD","SD","PA","ATP","DTP"]},
    {"name": "Examination by Concerned Circle - Senior Town Planner office", "sub_steps": ["Examination by Concerned Circle - Senior Town Planner office","Compilation of observations", "Site reports receival"], "approval": ["JD","ATP","STP"]},
    {"name": "Examination by SE / Executive Engineer - HSVP", "sub_steps": ["Examination by SE / Executive Engineer - HSVP","Compilation of observations", "Site reports receival"], "approval": ["JD","SDM","HDM","CHD","SDE","CHD","SDO","XEN","SE","CE","SE"]},
    {"name": "Examination by Fire Officer, Urban Local Bodies", "sub_steps": ["Examination by Fire Officer, Urban Local Bodies","Compilation of observations", "Site reports receival"], "approval": ["ASST.","SUPDT.","CONSULTANT","FIRE OFFICER"]},
    {"name": "Compilation of Reports in o/o DTCP", "sub_steps": ["Compilation of Reports in o/o DTCP"], "approval": ["JD","PA","ATP","DTP","ARCHITECT","STP","ARCHITECT","CTP","DTP"]},
    {"name": "Fixing of Meeting of BPAC to review the comments / report of all above", "sub_steps": ["Fixing of Meeting of BPAC to review the comments / report of all above"], "approval": ["STP"]},
    {"name": "Plan reviewed in BPAC Committee", "sub_steps": ["Plan reviewed in BPAC Committee"], "approval": ["o/o DTCP"]},
    {"name": "Observations conveyed", "sub_steps": ["Observations conveyed"]},
    {"name": "Resubmission of Dwgs after compliance", "sub_steps": ["Resubmission of Dwgs after compliance"]},
    {"name": "Circulation of BPs to STP (circle)GGN, SE-HSVP, Fire officer-ULB, Pkl for signatures.", "sub_steps": ["Circulation of BPs to STP (circle)GGN, SE-HSVP, Fire officer-ULB, Pkl for signatures."]},
    {"name": "Examination of BPs at Field offices", "sub_steps": ["Examination of BPs at Field offices"]},
    {"name": "Compilation of Reports in o/o DTCP", "sub_steps": [], "approval": ["JD"]},
    {"name": "Verification of the Licence / CLU permission / pending dues by the Department", "sub_steps": [], "approval": ["SO","AO","CAO"]},
    {"name": "Approved Building Plans & BR-III issued", "sub_steps": [], "approval": ["JD","ATP","DTP","ARCHITECT","STP","CTP"]}
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

root = tk.Tk()
root.title("Projects")
root.geometry('400x400')


def showProjectList():
    cursor.execute("SELECT name FROM projectList")
    rows = cursor.fetchall()
    project_names = [row[0] for row in rows]

    window = tk.Toplevel(root)
    window.title("Project List")

    for project_name in project_names:
        newButton = tk.Button(window, text=project_name, command=lambda name=project_name: openProject(name))
        newButton.pack()


def openStepDetails(project_name, step_name, sub_steps, approvals):
    def markCompleted(step, sub_step, completed):
        cursor.execute(f'''
        UPDATE progress_{project_name} 
        SET completed = ? 
        WHERE step = ? AND sub_step = ?
        ''', (completed, step, sub_step))
        conn.commit()

    window = tk.Toplevel(root)
    window.title(f"Step Details: {step_name}")

    step_frame = tk.LabelFrame(window, text="Sub-Steps")
    step_frame.pack(fill="both", expand="yes")

    for sub_step in sub_steps:
        var = tk.BooleanVar()
        cursor.execute(f'''
        SELECT completed FROM progress_{project_name} 
        WHERE step = ? AND sub_step = ?
        ''', (step_name, sub_step))
        result = cursor.fetchone()
        if result:
            var.set(result[0])
        else:
            cursor.execute(f'''
            INSERT INTO progress_{project_name} (step, sub_step, created_time, target_time, actual_time, document_path, completed) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (step_name, sub_step, time.time(), time.time() + 7.862e+6, None, None, False))
            conn.commit()

        checkbox = tk.Checkbutton(step_frame, text=sub_step, variable=var,
                                  command=lambda s=step_name, ss=sub_step, v=var: markCompleted(s, ss, v.get()))
        checkbox.pack()

    approval_frame = tk.LabelFrame(window, text="Approvals")
    approval_frame.pack(fill="both", expand="yes")

    for approval in approvals:
        var = tk.BooleanVar()
        cursor.execute(f'''
        SELECT completed FROM progress_{project_name} 
        WHERE step = ? AND sub_step = ?
        ''', (step_name, approval))
        result = cursor.fetchone()
        if result:
            var.set(result[0])
        else:
            cursor.execute(f'''
            INSERT INTO progress_{project_name} (step, sub_step, created_time, target_time, actual_time, document_path, completed) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (step_name, approval, time.time(), time.time() + 7.862e+6, None, None, False))
            conn.commit()

        checkbox = tk.Checkbutton(approval_frame, text=approval, variable=var,
                                  command=lambda s=step_name, ss=approval, v=var: markCompleted(s, ss, v.get()))
        checkbox.pack()


def openProject(project_name):
    window = tk.Toplevel(root)
    window.title(f"Project: {project_name}")

    for step in steps:
        step_button = tk.Button(window, text=step['name'],
                                command=lambda s=step: openStepDetails(project_name, s['name'], s['sub_steps'], s.get('approval', [])))
        step_button.pack(fill="both", expand="yes")


def projectTop():
    def addProject(name, desc, topl):
        cursor.execute(f"INSERT INTO projectList (name, desc, created_time, estimated_time) VALUES (?, ?, ?, ?)", (name, desc, time.time(), time.time() + 7.862e+6))
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
            completed BOOLEAN
        )
        ''')
        conn.commit()
        projectAdded = tk.Toplevel(topl)
        projectAdded.title("Project Added")
        newLabel = tk.Label(projectAdded, text="Project Added")
        newLabel.pack()

    window = tk.Toplevel(root)
    window.title("Creating New Project")

    projectName_label = tk.Label(window, text="Project Name:")
    projectName_label.pack()
    projectName_entry = tk.Entry(window)
    projectName_entry.pack()

    projectDesc_label = tk.Label(window, text="Project Description:")
    projectDesc_label.pack()
    projectDesc_entry = tk.Entry(window)
    projectDesc_entry.pack()

    projectSave_button = tk.Button(window, text="Save Entries", command=lambda: addProject(projectName_entry.get(), projectDesc_entry.get(), window))
    projectSave_button.pack()

    window.mainloop()


createProject_button = tk.Button(root, text="Create New Project", command=projectTop)
createProject_button.pack()

showProjects_button = tk.Button(root, text="Show Projects", command=showProjectList)
showProjects_button.pack()

root.mainloop()
