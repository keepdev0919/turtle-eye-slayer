from PIL import Image
import os
import shutil

# Paths
BRAIN_DIR = os.getenv("BRAIN_DIR", "/Users/choikjun/.gemini/antigravity/brain/5dd0f1ef-3eaf-4f15-bb14-988d3c8f58c9")
COMPOSITE_SRC = os.path.join(BRAIN_DIR, "demon_slayer_ui_assets_1765697959164.png")
CLEAN_SCROLL_SRC = os.path.join(BRAIN_DIR, "clean_scroll_v2_1765718091536.png")
ASSETS_DIR = "assets"

def make_transparent_and_trim(img, tolerance=40):
    img = img.convert("RGBA")
    datas = img.getdata()
    
    # Sample Top-Left for background color
    bg_color = datas[0]
    bg_rgb = bg_color[:3]
    
    new_data = []
    for item in datas:
        # Distance check
        diff = abs(item[0] - bg_rgb[0]) + abs(item[1] - bg_rgb[1]) + abs(item[2] - bg_rgb[2])
        is_white = item[0] > 240 and item[1] > 240 and item[2] > 240
        
        if diff < tolerance or is_white:
             new_data.append((255, 255, 255, 0))
        else:
             new_data.append(item)
    
    img.putdata(new_data)
    
    # Trim
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
        
    return img

def restore():
    print("Restoring assets...")
    
    # 1. Restore Red Banner (Main) from Composite
    if os.path.exists(COMPOSITE_SRC):
        full_img = Image.open(COMPOSITE_SRC)
        w, h = full_img.size
        # Crop Banner Area (Approx 46% to 59% height)
        banner = full_img.crop((0, int(h * 0.46), w, int(h * 0.59)))
        banner = make_transparent_and_trim(banner)
        
        save_path = os.path.join(ASSETS_DIR, "btn_main.png")
        banner.save(save_path)
        print(f"Restored {save_path} from composite.")
    else:
        print(f"Error: Composite source not found at {COMPOSITE_SRC}")

    # 2. Restore Green/Beige Scroll (Sub) from Clean Source
    if os.path.exists(CLEAN_SCROLL_SRC):
        # Load and ensure transparency (the generated file has white bg)
        scroll = Image.open(CLEAN_SCROLL_SRC)
        scroll = make_transparent_and_trim(scroll)
        
        save_path = os.path.join(ASSETS_DIR, "btn_sub.png")
        scroll.save(save_path)
        print(f"Restored {save_path} from clean v2 source.")
    else:
        print(f"Error: Clean scroll source not found at {CLEAN_SCROLL_SRC}")

if __name__ == "__main__":
    restore()
