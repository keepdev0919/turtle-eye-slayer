from PIL import Image
import os

source_path = "/Users/choikjun/.gemini/antigravity/brain/34606ccb-a17b-4707-8a29-d3b49aa05fdc/ui_frame_redone_1765622133909.png"
target_path = "assets/ui_frame.png"

def make_transparent(src, dest):
    print(f"Processing {src}...")
    img = Image.open(src)
    img = img.convert("RGBA")
    datas = img.getdata()
    
    new_data = []
    # Threshold for "black" to be transparent
    for item in datas:
        # Check if pixel is dark (black-ish)
        if item[0] < 50 and item[1] < 50 and item[2] < 50:
            new_data.append((0, 0, 0, 0)) # Transparent
        else:
            new_data.append(item)
            
    img.putdata(new_data)
    img.save(dest, "PNG")
    print(f"Saved transparent frame to {dest}")

if __name__ == "__main__":
    make_transparent(source_path, target_path)
