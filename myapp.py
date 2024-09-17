import re
import tkinter as tk
from tkinterdnd2 import TkinterDnD, DND_FILES
import os
import json

# Ensure the proper path for TkinterDnD library
os.environ['TKDND_LIBRARY'] = os.path.join(os.path.dirname(__file__), 'tkdnd2.9.2')

# Function to load config file
def load_config():
    config_path = os.path.join(os.getcwd(), "config.json")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as config_file:
            config = json.load(config_file)
        return config
    else:
        # Default values if config.json is not found
        return {"old_word": "", "new_word": "", "swap_mode": False}

# Function to replace words and preserve case
def replace_word(content, old_word, new_word, swap_mode=False):
    def replace_case(word, replacement_word):
        if word.isupper():
            return replacement_word.upper()
        elif word[0].isupper():
            return replacement_word.capitalize()
        else:
            return replacement_word.lower()

    old_is_phrase = " " in old_word
    new_is_phrase = " " in new_word

    replacement_count_old_to_new = 0  # Count replacements old_word -> new_word
    replacement_count_new_to_old = 0  # Count replacements new_word -> old_word (swap mode)

    if swap_mode:
        def swap(match):
            nonlocal replacement_count_old_to_new, replacement_count_new_to_old
            phrase = match.group(0)
            if phrase.lower() == old_word.lower():
                replacement_count_old_to_new += 1
                return replace_case(phrase, new_word)
            elif phrase.lower() == new_word.lower():
                replacement_count_new_to_old += 1
                return replace_case(phrase, old_word)
            return phrase

        pattern = f'({re.escape(old_word)}|{re.escape(new_word)})' if old_is_phrase or new_is_phrase else rf'\b({re.escape(old_word)}|{re.escape(new_word)})\b'
        modified_content = re.sub(pattern, swap, content, flags=re.IGNORECASE)
    else:
        pattern = re.escape(old_word) if old_is_phrase else rf'\b{re.escape(old_word)}\b'
        modified_content = re.sub(pattern, lambda match: replace_case(match.group(0), new_word), content, flags=re.IGNORECASE)
        replacement_count_old_to_new = len(re.findall(pattern, content, flags=re.IGNORECASE))

    return modified_content, replacement_count_old_to_new, replacement_count_new_to_old

# Handle the drag-and-drop of files
def handle_file(event):
    filepath = event.data
    filepath = filepath.strip('{}')  # Remove extra braces on some platforms
    process_file(filepath)

# Process the file and replace phrases or words
def process_file(filepath):
    # Get the current inputs from the GUI (not from config)
    old_phrase = entry_find.get()  # Use the input from the entry field
    new_phrase = entry_replace.get()  # Use the input from the entry field
    swap_mode = bool(swap_var.get())  # Use the current swap mode from the checkbox

    # Open and read the content of the file
    with open(filepath, "r", encoding="utf-8") as file:
        content = file.read()

    # Perform the phrase or word replacement
    modified_content, count_old_to_new, count_new_to_old = replace_word(content, old_phrase, new_phrase, swap_mode=swap_mode)

    # Save the modified file
    with open(filepath, "w", encoding="utf-8") as file:
        file.write(modified_content)

    # Update the status label with replacement counts
    if swap_mode:
        label_status.config(
            text=f"File processed: {os.path.basename(filepath)}.\nReplacements: {old_phrase} -> {new_phrase}: {count_old_to_new}, {new_phrase} -> {old_phrase}: {count_new_to_old}")
    else:
        label_status.config(
            text=f"File processed: {os.path.basename(filepath)}.\nReplacements: {old_phrase} -> {new_phrase}: {count_old_to_new}")

# Create the Tkinter GUI
root = TkinterDnD.Tk()
root.title("Text Replacer")
root.geometry("400x250")
root.wm_attributes("-topmost", 1)  # Keep the window on top

# Load default settings from config file
config = load_config()

# Add labels and entry fields for input
label_find = tk.Label(root, text="Word to find:")
label_find.pack(pady=5)
entry_find = tk.Entry(root)
entry_find.insert(0, config["old_word"])  # Preload with value from config
entry_find.pack(pady=5)

label_replace = tk.Label(root, text="Word to replace with:")
label_replace.pack(pady=5)
entry_replace = tk.Entry(root)
entry_replace.insert(0, config["new_word"])  # Preload with value from config
entry_replace.pack(pady=5)

# Add a checkbox for swap mode, with default based on config
swap_var = tk.IntVar(value=1 if config["swap_mode"] else 0)
check_swap = tk.Checkbutton(root, text="Swap mode (two-way replace)", variable=swap_var)
check_swap.pack(pady=5)

label_status = tk.Label(root, text="Drop a .txt file here")
label_status.pack(pady=20)

# Enable drag-and-drop for files
root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', handle_file)

# Start the Tkinter main loop
root.mainloop()
