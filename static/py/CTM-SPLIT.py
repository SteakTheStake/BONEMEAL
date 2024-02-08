import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk
from tkinter import messagebox
import os
from collections import defaultdict

# --- Functions for CTM.pyw functionality ---
def ensure_directory(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    pass

def split_image(image_paths_group, rows, cols):
    ensure_directory("assets/minecraft/optifine/ctm")
    
    for root_name, image_paths in image_paths_group.items():
        # Create a sub-folder named after the root name of the image group
        output_subfolder = os.path.join("assets/minecraft/optifine/ctm", root_name)
        ensure_directory(output_subfolder)
        
        for suffix, image_path in image_paths.items():
            img = Image.open(image_path)
            width, height = img.size
            tile_width = width // cols
            tile_height = height // rows
            
            total_tiles = rows * cols
            current_tile = 0

            for i in range(0, rows):
                for j in range(0, cols):
                    left = j * tile_width
                    upper = i * tile_height
                    right = left + tile_width
                    lower = upper + tile_height
                    
                    img_cropped = img.crop((left, upper, right, lower))
                    output_path = os.path.join(output_subfolder, f"{current_tile}{suffix}.png")
                    img_cropped.save(output_path)
                    
                    print(f"Progress: {current_tile}/{total_tiles} tiles processed for {root_name}{suffix}.")
                    current_tile += 1
    pass

def browse_images(suffix):
    file_paths = filedialog.askopenfilenames(filetypes=[("PNG files", "*.png")])
    if not file_paths:
        return
    
    img_frame = img_frames[suffix]
    for widget in img_frame.winfo_children():
        widget.destroy()
    
    for file_path in file_paths:
        img = Image.open(file_path)
        img = img.resize((50, 50))
        img = ImageTk.PhotoImage(img)
        
        lbl = ttk.Label(img_frame, image=img)
        lbl.image = img
        lbl.pack(side=tk.LEFT)
    
    img_frames[suffix].file_paths = file_paths
    pass

def execute_split():
    rows = int(rows_entry.get())
    cols = int(cols_entry.get())
    
    grouped_images = defaultdict(dict)
    
    for suffix, frame in img_frames.items():
        if hasattr(frame, "file_paths"):
            for file_path in frame.file_paths:
                root_name = os.path.splitext(os.path.basename(file_path))[0].replace("_n", "").replace("_s", "")
                grouped_images[root_name][suffix] = file_path

    split_image(grouped_images, rows, cols)
    pass

# --- Function for CTM-PROP.pyw functionality ---
def save_properties():

    selected_ctm_method = ctm_method_var.get()
    
    properties_text = f"method={selected_ctm_method}\n"

    # Add other fields here as you build up the GUI
    # For example, if you add an entry for `tiles`:
    # tiles_value = tiles_entry.get()
    # properties_text += f"tiles={tiles_value}\n"

    
    selected_folder = folder_var.get()
    filename = filename_entry.get()
    
    if selected_folder == "Select folder":
        messagebox.showwarning("Warning", "Please select a folder.")
        return
    
    if filename == "Enter filename":
        messagebox.showwarning("Warning", "Please enter a filename.")
        return
    
    
    selected_folder = folder_var.get()
    
    if selected_folder == "Select folder":
        messagebox.showwarning("Warning", "Please select a folder.")
        return
    
    
    width = width_entry.get()
    height = height_entry.get()

    output_path = os.path.join("assets/minecraft/optifine/ctm", selected_folder, f"{filename}.properties")


    
    selected_folder = folder_var.get()
    
    if selected_folder == "Select folder":
        messagebox.showwarning("Warning", "Please select a folder.")
        return
    
    
    width = width_entry.get()
    height = height_entry.get()
    
    if width:
        properties_text += f"width={width}\n"
    if height:
        properties_text += f"height={height}\n"

    output_path = os.path.join("assets/minecraft/optifine/ctm", selected_folder, f"{filename}.properties")

    
    # Reading the selected dropdown value and the entered text
    match_type = selected_match.get()
    match_value = match_value_entry.get()

    # Adding the match_type and match_value to the properties text
    properties_text += f"{match_type}{match_value}\n"


    tiles_input0 = tiles_input0_entry.get()
    tiles_input1 = tiles_input1_entry.get()
    if tiles_input0 and tiles_input1:
        properties_text += f"tiles={tiles_input0}-{tiles_input1}\n"

    if not output_path:
        return
    
    with open(output_path, "w") as file:
        file.write(properties_text)
    
    messagebox.showinfo("Success", "Properties file has been saved.")
    pass

# --- Main Application Window ---
root = tk.Tk()
root.title("Complete CTM Toolkit")

# Create frames for each set of functionality
ctm_frame = tk.Frame(root, padx=10, pady=10)
ctm_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

ctm_prop_frame = tk.Frame(root, padx=10, pady=10)
ctm_prop_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Add widgets for CTM.pyw functionality to ctm_frame
# Your CTM.pyw widgets and functionalities here

suffices = ["", "_n", "_s"]
img_frames = {}

for idx, suffix in enumerate(suffices):
    btn = ttk.Button(ctm_frame, text=f"Browse Texture{suffix}", command=lambda suffix=suffix: browse_images(suffix))
    btn.grid(row=0, column=idx, padx=10, pady=10)
    
    frame = tk.Frame(ctm_frame)
    frame.grid(row=1, column=idx, padx=10, pady=10)
    img_frames[suffix] = frame

rows_label = ttk.Label(ctm_frame, text="Rows:")
rows_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

rows_entry = ttk.Entry(ctm_frame)
rows_entry.grid(row=2, column=1, columnspan=2, padx=10, pady=5, sticky="e")

cols_label = ttk.Label(ctm_frame, text="Columns:")
cols_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")

cols_entry = ttk.Entry(ctm_frame)
cols_entry.grid(row=3, column=1, columnspan=2, padx=10, pady=5, sticky="e")

split_button = ttk.Button(ctm_frame, text="Split Image", command=execute_split)
split_button.grid(row=4, column=1, padx=10, pady=10)
ctm_prop_frame
# Add widgets for CTM-PROP.pyw functionality to ctm_prop_frame
# Your CTM-PROP.pyw widgets and functionalities here

# Create a button to refresh the folder list
# refresh_button = tk.Button(root, text="Refresh", command=refresh_folders)
# refresh_button.pack()

# Initialize the folder list
# refresh_folders()

root.mainloop()
