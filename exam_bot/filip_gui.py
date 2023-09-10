import tkinter as tk
from tkinter import filedialog
import threading
import json
from sender import send_command

class ExpandableListApp:
    def __init__(self, root):
        self.lock = threading.Lock()
        self.frame = tk.Frame(root)
        self.frame.pack()

        self.entries_frame = tk.Frame(self.frame)
        self.entries_frame.pack()

        self.control_frame = tk.Frame(self.frame)
        self.control_frame.pack()

        self.add_button = tk.Button(self.control_frame, text="Add Entry", command=self.add_entry)
        self.add_button.grid(row=0, column=0)

        self.save_button = tk.Button(self.control_frame, text="Save State", command=self.save_state)
        self.save_button.grid(row=0, column=1)

        self.load_state()

    def add_entry(self, file_name=None, status=None):
        entry_frame = tk.Frame(self.entries_frame)
        entry_frame.pack(fill=tk.X)

        if file_name is None:
            file_path = filedialog.askopenfilename()
            file_name = file_path.split("/")[-1].rstrip('.py')

        label = tk.Label(entry_frame, text=file_name, width=15, anchor='w')
        label.grid(row=0, column=0, sticky='w')

        button1 = tk.Button(entry_frame, text="Load", command=lambda: self.update_status(file_name, status_label, "Load"), activebackground='#00ff00')
        button1.grid(row=0, column=1)
        
        button2 = tk.Button(entry_frame, text="Unload", command=lambda: self.update_status(file_name, status_label, "Unload"), activebackground='#ff0000')
        button2.grid(row=0, column=2)

        button3 = tk.Button(entry_frame, text="Reload", command=lambda: self.update_status(file_name, status_label, "Reload"), activebackground='#0000ff')
        button3.grid(row=0, column=3)

        button4 = tk.Button(entry_frame, text="Delete", command=lambda: entry_frame.destroy())
        button4.grid(row=0, column=4)

        initial_status = f"Status: {status}" if status else "Status: None"
        status_label = tk.Label(entry_frame, text=initial_status, width=20, anchor='e')
        status_label.grid(row=0, column=5)

    def update_status(self, file_name, status_label, status):
        def task():
            status_label.config(text=f"Status: Processing")
            with self.lock:
                succ = send_command(f"{status} cogs.{file_name}")
                if succ == "fail":
                    status_label.config(text=f"Status: Failed")
                else:
                    status_label.config(text=f"Status: {status} {succ}")
        threading.Thread(target=task).start()

    def save_state(self):
        state = []
        for frame in self.entries_frame.winfo_children():
            try:
                file_name = frame.winfo_children()[0].cget("text")
                status_label = frame.winfo_children()[-1]
                status = status_label.cget("text").split(": ")[1]
                state.append({'file_name': file_name, 'status': status})
            except Exception as e:
                print(f"An error occurred while saving: {str(e)}")

        with open("state.json", "w") as f:
            json.dump(state, f)

    def load_state(self):
        try:
            with open("state.json", "r") as f:
                state = json.load(f)
            for entry in state:
                self.add_entry(entry['file_name'], entry['status'])
        except FileNotFoundError:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpandableListApp(root)
    root.mainloop()
