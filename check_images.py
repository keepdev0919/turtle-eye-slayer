from PIL import Image
import os

assets_dir = "assets"
for filename in os.listdir(assets_dir):
    if filename.endswith(".png"):
        path = os.path.join(assets_dir, filename)
        try:
            img = Image.open(path)
            has_transparency = False
            if img.mode == 'P':
                transparent = img.info.get("transparency", -1)
                for _, index in img.getcolors():
                    if index == transparent:
                        has_transparency = True
            elif img.mode == 'RGBA':
                extrema = img.getextrema()
                if extrema[3][0] < 255:
                    has_transparency = True
            
            print(f"{filename}: Mode={img.mode}, Transparent={has_transparency}")
        except Exception as e:
            print(f"{filename}: Error {e}")
