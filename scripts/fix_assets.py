from PIL import Image
import os
import shutil

# Paths
# Paths - Fallback to relative or current if developer path missing
BRAIN_DIR = os.getenv("BRAIN_DIR", "/Users/choikjun/.gemini/antigravity/brain/5dd0f1ef-3eaf-4f15-bb14-988d3c8f58c9")
CLEAN_SCROLL_SRC = os.path.join(BRAIN_DIR, "clean_scroll_v2_1765718091536.png")
ASSETS_DIR = "assets"
BANNER_PATH = os.path.join(ASSETS_DIR, "btn_main.png")
SCROLL_DEST = os.path.join(ASSETS_DIR, "btn_sub.png")

def clean_white_and_trim(img_path):
    if not os.path.exists(img_path):
        print(f"File not found: {img_path}")
        return

    try:
        img = Image.open(img_path).convert("RGBA")
        datas = img.getdata()
        
        # Sample background color from top-left corner
        bg_color = datas[0]
        # Ignore alpha in sample if present, we care about RGB match
        bg_rgb = bg_color[:3]
        
        print(f"Sampling background from {img_path}: {bg_rgb}")
        
        new_data = []
        tolerance = 40 # Increased tolerance
        
        for item in datas:
            # Euclidean distance approximation check
            # abs(r-r) + abs(g-g) + abs(b-b) is Manhattan, simpler and good enough here
            diff = abs(item[0] - bg_rgb[0]) + abs(item[1] - bg_rgb[1]) + abs(item[2] - bg_rgb[2])
            
            # Additional check: If pixel is very bright white, treat as bg regardless of sample
            # (In case sample is slightly off-white but image has pure whites)
            is_white = item[0] > 240 and item[1] > 240 and item[2] > 240
            
            if diff < tolerance or is_white:
                new_data.append((255, 255, 255, 0)) # Transparent
            else:
                new_data.append(item)
        
        img.putdata(new_data)
        
        # Trim (Crop to content)
        bbox = img.getbbox()
        if bbox:
            img = img.crop(bbox)
            print(f"Trimmed {img_path} to {bbox}")
        
        img.save(img_path, "PNG")
        print(f"Successfully processed {img_path}")
        
    except Exception as e:
        print(f"Error processing {img_path}: {e}")

def main():
    # 1. Replace Scroll with Clean Version (Option B)
    if os.path.exists(CLEAN_SCROLL_SRC):
        shutil.copy(CLEAN_SCROLL_SRC, SCROLL_DEST)
        print(f"Replaced scroll with clean version: {SCROLL_DEST}")
        # Process it too to ensure transparency
        clean_white_and_trim(SCROLL_DEST)
    else:
        print("Clean scroll source not found!")

    # 2. Fix Red Banner (Trim White Box)
    clean_white_and_trim(BANNER_PATH)

if __name__ == "__main__":
    main()
