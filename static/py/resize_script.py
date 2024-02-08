import os
import sys
from PIL import Image

# Blacklisted directories
BLACKLISTED_DIRS = [
    '/assets/minecraft/textures/environment',
    '/assets/minecraft/textures/font',
    '/assets/minecraft/textures/gui',
    '/assets/minecraft/textures/misc'
]


def resize_image(image_path, percentage):
    try:
        img = Image.open(image_path)
        width, height = img.size
        new_width = int(width * percentage / 100)
        new_height = int(height * percentage / 100)
        img_resized = img.resize((new_width, new_height), Image.Resampling.NEAREST)
        img_resized.save(image_path)
        return f"Resized {image_path}"
    except Exception as e:
        return f"Error resizing {image_path}: {e}"


def resize_images_in_tree(folder_path, percentage):
    messages = []
    for root, dirs, files in os.walk(folder_path):
        if any(root.endswith(blacklist) for blacklist in BLACKLISTED_DIRS):
            messages.append(f"Skipping blacklisted directory: {root}")
            continue
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff')):
                image_path = os.path.join(root, file)
                message = resize_image(image_path, percentage)
                messages.append(message)
    return messages


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python resize_script.py <folder_path> <percentage>")
        sys.exit(1)

    folder_path = sys.argv[1]
    percentage = float(sys.argv[2])

    if not (0 < percentage <= 100):
        print("Invalid percentage. Enter a number between 0 and 100.")
        sys.exit(1)

    resize_results = resize_images_in_tree(folder_path, percentage)
    for result in resize_results:
        print(result)
