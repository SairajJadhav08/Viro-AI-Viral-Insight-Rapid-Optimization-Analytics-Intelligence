"""
Embed patent figure images as base64 data URIs into VIRO-AI_Patent_Figures_Gallery.md
so the document is self-contained and displays images without external folder.
Run from project root: python scripts/embed_gallery_images.py
"""
import os
import base64
import re

# Project root (parent of scripts/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GALLERY_MD = os.path.join(PROJECT_ROOT, "docs", "VIRO-AI_Patent_Figures_Gallery.md")
FIGURES_DIR = os.path.join(PROJECT_ROOT, "patent_figures_colourful")

def main():
    if not os.path.isfile(GALLERY_MD):
        # Fallback if gallery still at root
        alt = os.path.join(PROJECT_ROOT, "VIRO-AI_Patent_Figures_Gallery.md")
        if os.path.isfile(alt):
            global GALLERY_MD
            GALLERY_MD = alt
    with open(GALLERY_MD, "r", encoding="utf-8") as f:
        content = f.read()

    # Find all markdown image refs: ![alt](patent_figures_colourful/Figure_XX....png) or ../patent_figures_colourful/
    pattern = re.compile(
        r'(!\[[^\]]*\]\()(?:\.\./)?(patent_figures_colourful/([^)]+\.png))(\))',
        re.IGNORECASE
    )

    def replace_with_base64(match):
        prefix = match.group(1)
        path = match.group(2)
        filename = match.group(3)
        suffix = match.group(4)
        full_path = os.path.join(PROJECT_ROOT, path.replace("/", os.sep))
        if not os.path.isfile(full_path):
            print(f"SKIP (not found): {full_path}")
            return match.group(0)
        with open(full_path, "rb") as img:
            b64 = base64.b64encode(img.read()).decode("ascii")
        data_uri = f"data:image/png;base64,{b64}"
        print(f"Embedded: {filename} ({len(b64)//1024} KB base64)")
        return f"{prefix}{data_uri}{suffix}"

    new_content = pattern.sub(replace_with_base64, content)

    with open(GALLERY_MD, "w", encoding="utf-8") as f:
        f.write(new_content)

    print("Done. VIRO-AI_Patent_Figures_Gallery.md now contains embedded images.")

if __name__ == "__main__":
    main()
