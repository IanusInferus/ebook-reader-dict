import re
import os
from pathlib import Path
from lxml import etree

# Path to your OEBPS folder
oebps_dir = Path("data/en/en/output/mobi/dict-data.mobi/OEBPS")

# Size limit
MAX_SIZE = 14 * 1024  # KiB

def extract_word(entry_content: str) -> str:
    """Extract the dictionary word from an <idx:entry> block."""
    match = re.search(r"<idx:orth[^>]*>(.*?)</idx:orth>", entry_content, flags=re.DOTALL | re.IGNORECASE)
    if not match:
        return "Unknown"
    
    inner_text = match.group(1)
    # Remove all tags inside <idx:orth> (keep only text)
    clean_text = re.sub(r"<[^>]+>", "", inner_text)
    # Trim only the leading and trailing line breaks and spaces
    return clean_text.strip().replace('\n', ' ').replace('\r', ' ')

def is_well_formed_xhtml(file_name: str, xhtml_content: str) -> bool:
    try:
        etree.fromstring(xhtml_content.encode('utf-8'))
        return True
    except etree.XMLSyntaxError as e:
        print(f"{file_name} syntax error: {e}")
        return False

def find_big_entries():
    for file in sorted(oebps_dir.glob("g*.xhtml")):
        with file.open(encoding="utf-8") as f:
            content = f.read()
        is_well_formed_xhtml(file.name, content)

    for file in sorted(oebps_dir.glob("g*.xhtml")):
        # print(f"Checking {file.name}...")
        with file.open(encoding="utf-8") as f:
            content = f.read()

        # Split by <idx:entry> (each entry starts with this)
        entries = content.split("<idx:entry")

        # Skip first part (before first entry)
        for i, entry in enumerate(entries[1:], 1):
            entry_content = "<idx:entry" + entry
            size = len(entry_content.encode("utf-16"))

            if size > MAX_SIZE:
                # Try to extract the word for better reporting
                word = "Unknown"
                if "<idx:orth" in entry_content:
                    try:
                        word = extract_word(entry_content)
                    except Exception:
                        pass

                print(f"{file.name} entry #{i}: '{word}' - {size/1024:.1f} KiB")

if __name__ == "__main__":
    find_big_entries()
