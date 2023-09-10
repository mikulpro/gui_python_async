import tkinter as tk
from tkinter import filedialog
from sender import send_command
import threading

class ExpandableListApp:
    def __init__(self, root):
        self.frame = tk.Frame(root)
        self.frame.pack()
        self.lock = threading.Lock()
        
        self.add_button = tk.Button(self.frame, text="Add Entry", command=self.add_entry)
        self.add_button.pack()
        
        self.entries_frame = tk.Frame(self.frame)
        self.entries_frame.pack()

    def add_entry(self):
        entry_frame = tk.Frame(self.entries_frame)
        entry_frame.pack()

        file_path = filedialog.askopenfilename()
        file_name = file_path.split("/")[-1].rstrip('.py')
        
        label = tk.Label(entry_frame, text=file_name)
        label.pack(side=tk.LEFT)

        button1 = tk.Button(entry_frame, text="Load", command=lambda: self.update_status(file_name, status_label, "Loaded"))
        button1.pack(side=tk.LEFT)
        
        button2 = tk.Button(entry_frame, text="Unload", command=lambda: self.update_status(file_name, status_label, "Unloaded"))
        button2.pack(side=tk.LEFT)

        button3 = tk.Button(entry_frame, text="Reload", command=lambda: self.update_status(file_name, status_label, "Reloaded"))
        button3.pack(side=tk.LEFT)

        status_label = tk.Label(entry_frame, text="Status: None")
        status_label.pack(side=tk.LEFT)

    def update_status(self, file_name, status_label, status):
        def task():
            status_label.config(text=f"Status: Processing")
            with self.lock:  
                try:
                    if status == "Loaded":
                        succ = send_command(f"Load cogs.{file_name}")
                    elif status == "Unloaded":
                        succ = send_command(f"Unload cogs.{file_name}")
                    elif status == "Reloaded":
                        succ = send_command(f"Reload cogs.{file_name}")
                    
                    if succ == "fail":
                        status_label.config(text=f"Status: Failed")
                    else:
                        status_label.config(text=f"Status: {status} {succ}")
                except:
                    status_label.config(text=f"Status: Not Reachable")
        threading.Thread(target=task).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpandableListApp(root)
    root.mainloop()
