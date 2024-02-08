import os
import glob
import tkinter as tk
from tkinter import filedialog
from PIL import Image

def find_png_files(directory):
    """
    Find all .png files in the specified directory and its subdirectories.
    """
    return glob.glob(os.path.join(directory, '**/*.png'), recursive=True)

def convert_to_indexed_color(image_path):
    """
    Convert the image to indexed color and save it.
    """
    with Image.open(image_path) as img:
        img = img.convert('P', palette=Image.ADAPTIVE, colors=256)
        img.save(image_path)

def convert_all_images(directory):
    """
    Convert all .png images in the directory to indexed color.
    """
    for image_path in find_png_files(directory):
        convert_to_indexed_color(image_path)
        print(f'Converted: {image_path}')

def select_directory():
    """
    Open a dialog to select a directory and start the conversion process.
    """
    directory = filedialog.askdirectory()
    if directory:
        convert_all_images(directory)
        print("All images have been converted.")

# Tkinter GUI
root = tk.Tk()
root.title("PNG to Indexed Color Converter")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack(padx=10, pady=10)

btn_select_dir = tk.Button(frame, text="Select Directory", command=select_directory)
btn_select_dir.pack()

root.mainloop()
