import tkinter as tk
from tkinter import ttk, messagebox
from database import session, Task, LogEntry
from speech_handler import SpeechHandler
from datetime import datetime
from threading import Thread
import sys

class TaskManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Task Manager")
        self.root.geometry("800x600")
        
        self.speech = SpeechHandler()
        self.setup_gui()
        self.refresh_tasks()

    def setup_gui(self):
        # Configure style for rounded corners
        style = ttk.Style()
        style.configure("Rounded.TFrame", borderwidth=1, relief="solid")
        style.configure("Rounded.TButton", borderwidth=0, relief="flat", padding=5)
        style.configure("Title.TLabel", font=("Helvetica", 12, "bold"))
        
        # Main container with padding
        main_container = ttk.Frame(self.root, padding="20")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left side - Tasks
        left_frame = ttk.Frame(main_container, style="Rounded.TFrame")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Task header
        ttk.Label(left_frame, text="Tasks", style="Title.TLabel").pack(pady=(10, 5), padx=10)
        
        # Task controls
        task_controls = ttk.Frame(left_frame)
        task_controls.pack(fill=tk.X, pady=10, padx=10)
        
        ttk.Button(task_controls, text="Add Task", style="Rounded.TButton", 
                  command=self.show_add_task_dialog).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(task_controls, text="Complete Task", style="Rounded.TButton",
                  command=self.complete_selected_task).pack(side=tk.LEFT)
        
        # Tasks list with custom style
        self.tasks_list = ttk.Treeview(left_frame, columns=("Title", "Points", "Status"), 
                                     show="headings", height=15)
        self.tasks_list.heading("Title", text="Title")
        self.tasks_list.heading("Points", text="Points")
        self.tasks_list.heading("Status", text="Status")
        self.tasks_list.column("Title", width=200)
        self.tasks_list.column("Points", width=70)
        self.tasks_list.column("Status", width=100)
        self.tasks_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self.tasks_list.bind('<<TreeviewSelect>>', self.on_task_select)
        
        # Add scrollbar to tasks list
        tasks_scroll = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.tasks_list.yview)
        tasks_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, 10))
        self.tasks_list.configure(yscrollcommand=tasks_scroll.set)
        
        # Right side - Notes
        right_frame = ttk.Frame(main_container, style="Rounded.TFrame")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Notes header
        ttk.Label(right_frame, text="Task Notes", style="Title.TLabel").pack(pady=(10, 5), padx=10)
        
        # Notes controls
        notes_controls = ttk.Frame(right_frame)
        notes_controls.pack(fill=tk.X, pady=10, padx=10)
        
        self.record_button = ttk.Button(notes_controls, text="Start Recording", 
                                      style="Rounded.TButton", command=self.toggle_recording)
        self.record_button.pack(side=tk.LEFT)
        
        # Notes list with scrollbar
        notes_container = ttk.Frame(right_frame)
        notes_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.notes_text = tk.Text(notes_container, wrap=tk.WORD, height=10,
                                font=("Helvetica", 10))
        self.notes_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        notes_scroll = ttk.Scrollbar(notes_container, orient=tk.VERTICAL, 
                                   command=self.notes_text.yview)
        notes_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.notes_text.configure(yscrollcommand=notes_scroll.set)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, 
                                  relief=tk.GROOVE, padding=(5, 2))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def show_add_task_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Task")
        dialog.geometry("400x350")
        dialog.resizable(False, False)
        
        # Make dialog modal
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Main container with padding
        container = ttk.Frame(dialog, padding="20")
        container.pack(fill=tk.BOTH, expand=True)
        
        # Title section
        ttk.Label(container, text="Add New Task", style="Title.TLabel").pack(pady=(0, 15))
        
        # Task title
        ttk.Label(container, text="Task Title:").pack(anchor=tk.W)
        title_entry = ttk.Entry(container, width=40, font=("Helvetica", 10))
        title_entry.pack(fill=tk.X, pady=(5, 15))
        
        # Description
        ttk.Label(container, text="Description:").pack(anchor=tk.W)
        desc_container = ttk.Frame(container)
        desc_container.pack(fill=tk.BOTH, expand=True, pady=(5, 15))
        
        desc_text = tk.Text(desc_container, height=5, width=40, font=("Helvetica", 10),
                          wrap=tk.WORD)
        desc_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        desc_scroll = ttk.Scrollbar(desc_container, orient=tk.VERTICAL,
                                  command=desc_text.yview)
        desc_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        desc_text.configure(yscrollcommand=desc_scroll.set)
        
        # Buttons container
        button_container = ttk.Frame(container)
        button_container.pack(fill=tk.X, pady=(0, 10))
        
        def add_task():
            title = title_entry.get().strip()
            description = desc_text.get("1.0", tk.END).strip()
            
            if not title:
                messagebox.showerror("Error", "Task title is required!")
                return
                
            points = 10 if len(title.split()) > 3 else 5
            task = Task(
                title=title,
                description=description,
                points=points
            )
            session.add(task)
            session.commit()
            self.refresh_tasks()
            dialog.destroy()
        
        # Buttons with consistent styling
        ttk.Button(button_container, text="Add Task", style="Rounded.TButton",
                  command=add_task).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_container, text="Cancel", style="Rounded.TButton",
                  command=dialog.destroy).pack(side=tk.LEFT)

    def complete_selected_task(self):
        selection = self.tasks_list.selection()
        if not selection:
            messagebox.showinfo("Info", "Please select a task to complete")
            return
            
        task_id = int(selection[0])
        task = session.get(Task, task_id)
        if task:
            task.completed = True
            task.completed_at = datetime.now()
            session.commit()
            self.refresh_tasks()
            messagebox.showinfo("Success", f"Task completed! You earned {task.points} points!")

    def toggle_recording(self):
        selection = self.tasks_list.selection()
        if not selection:
            messagebox.showinfo("Info", "Please select a task to add a note to")
            return

        if not hasattr(self, 'recording_thread') or self.recording_thread is None or not self.recording_thread.is_alive():
            # Start recording
            self.record_button.configure(text="Stop Recording")
            self.status_var.set("Recording voice note... Click 'Stop Recording' when done.")
            self.root.update()
            
            self.speech.start_recording()
            self.recording_thread = Thread(target=self.speech.listen, daemon=True)
            self.recording_thread.start()
        else:
            # Stop recording
            self.record_button.configure(text="Start Recording")
            self.speech.is_recording = False
            content = self.speech.stop_recording()
            
            if content:
                task_id = int(selection[0])
                task = session.get(Task, task_id)
                if task:
                    note = LogEntry(content=content, task=task)  # Associate note with task
                    session.add(note)
                    session.commit()
                    task = session.get(Task, task_id)  # Refresh the task object to get updated notes
                    self.refresh_notes(task)
                    self.status_var.set("Voice note added successfully!")
            else:
                self.status_var.set("No speech detected or could not understand audio.")
            
            # Wait for the recording thread to finish
            if hasattr(self, 'recording_thread') and self.recording_thread is not None and self.recording_thread.is_alive():
                self.recording_thread.join(timeout=1)
            self.recording_thread = None

    def refresh_tasks(self):
        for item in self.tasks_list.get_children():
            self.tasks_list.delete(item)
            
        tasks = session.query(Task).all()
        for task in tasks:
            status = "Completed" if task.completed else "Pending"
            self.tasks_list.insert("", tk.END, iid=str(task.id), values=(task.title, task.points, status))

    def refresh_notes(self, task):
        self.notes_text.delete("1.0", tk.END)
        # Only show notes for the selected task
        for note in task.notes:
            self.notes_text.insert(tk.END, f"[{note.created_at.strftime('%Y-%m-%d %H:%M')}]\n")
            self.notes_text.insert(tk.END, f"{note.content}\n\n")

    def on_task_select(self, event):
        selection = self.tasks_list.selection()
        if selection:
            task_id = int(selection[0])
            task = session.get(Task, task_id)
            if task:
                self.refresh_notes(task)

    def cleanup(self):
        self.speech.cleanup()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = TaskManagerGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.cleanup)
    root.mainloop()

if __name__ == "__main__":
    main()
