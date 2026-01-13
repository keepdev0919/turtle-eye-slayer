from PIL import Image, ImageEnhance, ImageDraw
import os

ASSETS_DIR = "assets"
TARGETS = ["btn_main.png", "btn_sub.png"]

def flood_fill_transparency(img, tolerance=30):
    img = img.convert("RGBA")
    width, height = img.size
    
    # Get data
    pixels = img.load()
    
    # Helper to check color match
    def color_match(p1, p2):
        return abs(p1[0]-p2[0]) + abs(p1[1]-p2[1]) + abs(p1[2]-p2[2]) < tolerance

    # Start points (Corners)
    seeds = [(0, 0), (width-1, 0), (0, height-1), (width-1, height-1)]
    
    # BFS Flood Fill
    visited = set()
    queue = []
    
    # Initialize queue with matching corners
    bg_color = pixels[0, 0] # Assume top-left is BG
    
    for seed in seeds:
         # Check if seed matches approximate BG color
        if color_match(pixels[seed], bg_color):
            queue.append(seed)
            visited.add(seed)

    while queue:
        x, y = queue.pop(0)
        pixels[x, y] = (0, 0, 0, 0) # Make transparent

        # Check neighbors
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                if color_match(pixels[nx, ny], bg_color):
                    visited.add((nx, ny))
                    queue.append((nx, ny))
    
    return img

def process_image(filename):
    path = os.path.join(ASSETS_DIR, filename)
    if not os.path.exists(path):
        print(f"Skipping {filename}: Not found")
        return

    try:
        print(f"Processing {filename}...")
        img = Image.open(path)
        
        # 1. Transparency (Flood Fill is safer for user screenshots/images)
        img = flood_fill_transparency(img)
        
        # 2. Trim
        bbox = img.getbbox()
        if bbox:
            img = img.crop(bbox)
            print(f"  Trimmed to {bbox}")
            
        # 3. Polish (Slight Contrast & Sharpness)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.1) # 10% more contrast
        
        # Resize if massive (Keep within manageable UI bounds, e.g., max width 600)
        MAX_WIDTH = 600
        if img.width > MAX_WIDTH:
            ratio = MAX_WIDTH / img.width
            new_size = (MAX_WIDTH, int(img.height * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            print(f"  Resized to {new_size}")

        img.save(path)
        print(f"  Saved polished {filename}")
        
    except Exception as e:
        print(f"Failed to process {filename}: {e}")

if __name__ == "__main__":
    for t in TARGETS:
        process_image(t)
