import os
from tkinter import Tk, filedialog
from PIL import Image

def feather_edges(img):
    img = img.convert('RGBA')  # Ensure the image is in RGBA mode
    width, height = img.size
    feather_size = min(width, height) // 10

    mask = Image.new('L', (width, height), 0)
    for i in range(feather_size):
        shade = int(255 * (i / feather_size))
        mask.paste(shade, (i, 0, i+1, height))
        mask.paste(shade, (0, i, width, i+1))
        mask.paste(shade, (width - i, 0, width - i+1, height))
        mask.paste(shade, (0, height - i, width, height - i+1))

    flipped_lr = img.transpose(Image.FLIP_LEFT_RIGHT)
    flipped_tb = img.transpose(Image.FLIP_TOP_BOTTOM)
    img_blend_lr = Image.blend(img, flipped_lr, alpha=0.5)
    img_blend_final = Image.blend(img_blend_lr, flipped_tb, alpha=0.5)

    img_with_feathered_edges = Image.composite(img_blend_final, img, mask)
    return img_with_feathered_edges


def make_tileable(image_path, output_path):
    img = Image.open(image_path)
    img_feathered = feather_edges(img)
    img_feathered.save(output_path, 'PNG')

def find_png_files(directory):
    png_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.png'):
                png_files.append(os.path.join(root, file))
    return png_files

def convert_images(directory):
    png_files = find_png_files(directory)
    for file_path in png_files:
        make_tileable(file_path, file_path)  # Overwriting the original file

def select_directory():
    root = Tk()
    root.withdraw()
    directory = filedialog.askdirectory()
    root.destroy()
    return directory

def main():
    directory = select_directory()
    if directory:
        convert_images(directory)
        print("Conversion complete.")
    else:
        print("No directory selected.")

if __name__ == "__main__":
    main()
