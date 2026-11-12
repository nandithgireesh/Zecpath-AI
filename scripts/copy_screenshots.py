import os
import shutil
import glob

src_dir = r"C:\Users\hp\Pictures\Screenshots"
dst_dir = r"d:\Zecpath-AI - Copy\Day_28_LaTeX_Report\user_screenshots"
os.makedirs(dst_dir, exist_ok=True)

# Find screenshots from 12-09-2026 after 20:55
files = glob.glob(os.path.join(src_dir, "Screenshot 2026-09-12 2*.png"))
copied = []
for f in sorted(files):
    base = os.path.basename(f)
    size = os.path.getsize(f)
    if size > 5000:  # Skip empty or accidental screenshots
        dest = os.path.join(dst_dir, base)
        shutil.copy2(f, dest)
        copied.append((base, size))

print(f"Copied {len(copied)} screenshots:")
for name, sz in copied:
    print(f" - {name} ({sz} bytes)")
