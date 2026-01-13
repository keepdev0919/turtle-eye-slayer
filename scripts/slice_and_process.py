from PIL import Image
import os

SOURCE_PATH = os.getenv("SOURCE_PATH", "/Users/choikjun/.gemini/antigravity/brain/5dd0f1ef-3eaf-4f15-bb14-988d3c8f58c9/demon_slayer_ui_assets_1765697959164.png")
ASSETS_DIR = "assets"

def make_transparent(img, tolerance=30):
    img = img.convert("RGBA")
    datas = img.getdata()
    new_data = []
    # Assumes dark/black background for this specific generation
    for item in datas:
        # If deeply dark (black/dark grey), make transparent
        if item[0] < tolerance and item[1] < tolerance and item[2] < tolerance:
            new_data.append((0, 0, 0, 0))
        else:
            new_data.append(item)
    img.putdata(new_data)
    return img

def slice_and_process():
    if not os.path.exists(SOURCE_PATH):
        print(f"Error: Source file not found at {SOURCE_PATH}")
        return

    try:
        full_img = Image.open(SOURCE_PATH)
        w, h = full_img.size
        print(f"Loaded source image: {w}x{h}")
        
        # Hardcoded Vertical Slices based on visual inspection of the generation
        # Top: Background (approx top 45%)
        # Middle 1: Red Banner (approx 45% - 60%)
        # Middle 2: Scroll (approx 60% - 75%)
        # Bottom: Wood Sign (approx 75% - 90%)
        
        # 1. Background (Keep opaque)
        bg = full_img.crop((0, 0, w, int(h * 0.45)))
        bg.save(os.path.join(ASSETS_DIR, "bg_dojo.png"))
        print("Reference: Saved bg_dojo.png")
        
        # 2. Main Banner (Red) - Make Transparent
        # Crop slightly tighter horizontally to avoid edges if needed, but standard is fine
        banner = full_img.crop((0, int(h * 0.46), w, int(h * 0.59)))
        banner = make_transparent(banner)
        # Trim transparent borders
        banner = banner.crop(banner.getbbox())
        banner.save(os.path.join(ASSETS_DIR, "btn_main.png"))
        print("Reference: Saved btn_main.png")
        
        # 3. Scroll (Beige) - Make Transparent
        scroll = full_img.crop((0, int(h * 0.62), w, int(h * 0.77)))
        scroll = make_transparent(scroll)
        scroll = scroll.crop(scroll.getbbox())
        scroll.save(os.path.join(ASSETS_DIR, "btn_sub.png"))
        print("Reference: Saved btn_sub.png")
        
        # 4. Wood Sign - Make Transparent
        sign = full_img.crop((0, int(h * 0.80), w, h))
        sign = make_transparent(sign)
        bbox = sign.getbbox()
        if bbox:
            sign = sign.crop(bbox)
        sign.save(os.path.join(ASSETS_DIR, "sign_wood.png"))
        print("Reference: Saved sign_wood.png")
        
        print("Slicing complete.")
        
    except Exception as e:
        print(f"Failed to process: {e}")

if __name__ == "__main__":
    slice_and_process()
