import tkinter as tk
import os

def search_and_convert(directory):
    """Searches the specified directory for files with "_s.png" suffix and converts them to full opacity."""

    # Get a list of all files in the directory
    files = os.listdir(directory)

    # Iterate over the files
    for file in files:
        # Check if the file has "_s.png" suffix
        if file.endswith("_s.png"):
            # Get the full path to the file
            file_path = os.path.join(directory, file)

            # Open the file in binary mode
            with open(file_path, "rb") as f:
                # Read the file contents
                data = f.read()

            # Convert the data to a list of integers
            data_list = list(data)

            # Iterate over the data list in steps of 4 (RGBA values)
            for i in range(0, len(data_list), 4):
                # Set the alpha value to 255 (full opacity)
                data_list[i + 3] = 255

            # Convert the modified data list back to bytes
            data = bytes(data_list)

            # Open the file in binary mode for writing
            with open(file_path, "wb") as f:
                # Write the modified data to the file
                f.write(data)

    # Display a message indicating the conversion is complete
    tk.messagebox.showinfo("Conversion Complete", "All files with '_s.png' suffix have been converted to full opacity.")

def select_directory():
    """Opens a dialog to select a directory and returns the selected directory path."""

    # Create a Tkinter window
    window = tk.Tk()
    window.withdraw()

    # Open the directory selection dialog
    directory = tk.filedialog.askdirectory(title="Select Directory")

    # Close the Tkinter window
    window.destroy()

    # Return the selected directory path
    return directory

def main():
    """Gets the directory path from the user and calls the search_and_convert function to convert the files."""

    # Get the directory path from the user
    directory = select_directory()

    # Check if the directory is valid
    if directory:
        # Call the search_and_convert function to convert the files
        search_and_convert(directory)

if __name__ == "__main__":
    main()