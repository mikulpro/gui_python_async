import tkinter as tk
from tkinter import filedialog
import shutil
import os

class FileCopyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Copy App")
        
        self.source_file = None
        self.destination_dir = "D:/"  # Update this with your desired destination directory
        
        self.select_button = tk.Button(root, text="Select File", command=self.select_file)
        self.select_button.pack(pady=10)
        
        self.copy_button = tk.Button(root, text="Copy File", command=self.copy_file)
        self.copy_button.pack(pady=10)
    
    def select_file(self):
        self.source_file = filedialog.askopenfilename()
    
    def copy_file(self):
        if self.source_file is not None:
            try:
                copied_file = shutil.copy(self.source_file, self.destination_dir)
                self.set_file_permissions(copied_file)
                tk.messagebox.showinfo("Success", "File copied successfully!")
            except Exception as e:
                tk.messagebox.showerror("Error", f"An error occurred: {str(e)}")
        else:
            tk.messagebox.showwarning("Warning", "Please select a file first.")
    
    def set_file_permissions(self, file_path):
        try:
            # Replace '0o755' with the desired permissions (e.g., read-write-execute for owner, read-execute for others)
            os.chmod(file_path, 0o755)
        except Exception as e:
            print(f"Error setting permissions: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileCopyApp(root)
    root.mainloop()