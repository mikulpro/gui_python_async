import tkinter as tk
from tkinter import simpledialog

def get_name():
    name = simpledialog.askstring("Input", "Please enter your name:")
    if name:
        print(f"Hello, {name}!")
    else:
        print("You must enter your name.")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide the main application window

    get_name()

    root.mainloop()
