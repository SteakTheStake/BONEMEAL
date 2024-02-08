import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox

def select_source_directory():
    directory = filedialog.askdirectory()
    source_dir.set(directory)

def select_target_directory():
    directory = filedialog.askdirectory()
    target_dir.set(directory)

def copy_and_rename_files():
    source_directory = source_dir.get()
    target_directory = target_dir.get()

    if not os.path.exists(target_directory):
        os.makedirs(target_directory)

    for root, dirs, files in os.walk(source_directory):
        for file in files:
            if file in ["0.png", "0_n.png", "0_s.png"]:
                parent_dir = os.path.basename(root)
                new_file_name = file.replace("0", parent_dir)
                source_file = os.path.join(root, file)
                destination_file = os.path.join(target_directory, new_file_name)
                shutil.copy(source_file, destination_file)

    messagebox.showinfo("Info", "Files copied and renamed successfully!")

# Initialize Tkinter window
root = tk.Tk()
root.title("File Copy and Rename Tool")

source_dir = tk.StringVar()
target_dir = tk.StringVar()

# Create and place widgets
tk.Button(root, text="Select Source Directory", command=select_source_directory).pack()
tk.Label(root, textvariable=source_dir).pack()
tk.Button(root, text="Select Target Directory", command=select_target_directory).pack()
tk.Label(root, textvariable=target_dir).pack()
tk.Button(root, text="Copy and Rename Files", command=copy_and_rename_files).pack()

# Run the event loop
root.mainloop()
