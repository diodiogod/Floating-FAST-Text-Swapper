import tkinter as tk
from tkinterdnd2 import TkinterDnD, DND_FILES
import os
import re
import json
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

# Function to replace words and preserve case, and count replacements
def replace_word(content, old_word, new_word, swap_mode=False):
    def replace_case(word, replacement_word):
        if word.isupper():
            return replacement_word.upper()  # Keep replacement uppercase
        elif word[0].isupper():
            return replacement_word.capitalize()  # Capitalize the replacement
        else:
            return replacement_word.lower()  # Make replacement lowercase

    words = re.split(r'(\W+)', content)  # Split by non-word characters to preserve spaces and punctuation
    replacement_count_old_to_new = 0  # Counter for old_word -> new_word
    replacement_count_new_to_old = 0  # Counter for new_word -> old_word (swap mode)

    for i, word in enumerate(words):
        if swap_mode:
            # Swap both ways without looping
            if re.fullmatch(old_word, word, re.IGNORECASE):
                words[i] = replace_case(word, new_word)
                replacement_count_old_to_new += 1
            elif re.fullmatch(new_word, word, re.IGNORECASE):
                words[i] = replace_case(word, old_word)
                replacement_count_new_to_old += 1
        else:
            # Standard replacement from old_word to new_word
            if re.fullmatch(old_word, word, re.IGNORECASE):
                words[i] = replace_case(word, new_word)
                replacement_count_old_to_new += 1

    return ''.join(words), replacement_count_old_to_new, replacement_count_new_to_old  # Return modified content and counts

# Function that handles the file dropped
def handle_file(event):
    filepath = event.data.strip("{}")  # Get the file path and remove curly braces
    if filepath.lower().endswith(".txt"):
        with open(filepath, "r", encoding="utf-8") as file:
            content = file.read()

        # Get the words from the entry fields
        old_word = entry_find.get()
        new_word = entry_replace.get()

        # Check if swap mode is active
        swap_mode = swap_var.get() == 1

        # Replace the words (and swap if necessary)
        modified_content, count_old_to_new, count_new_to_old = replace_word(content, old_word, new_word, swap_mode=swap_mode)

        # Save the file automatically
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(modified_content)

        # Update the status label with detailed counts
        if swap_mode:
            label_status.config(
                text=f"File processed: {os.path.basename(filepath)}. Replacements: {old_word}->{new_word}: {count_old_to_new}, {new_word}->{old_word}: {count_new_to_old}")
        else:
            label_status.config(
                text=f"File processed: {os.path.basename(filepath)}. Replacements: {old_word}->{new_word}: {count_old_to_new}")

# Create a floating, draggable window with tkinter
root = TkinterDnD.Tk()  # Use TkinterDnD for drag-and-drop
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

# Enable the window to accept drag-and-drop of files
root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', handle_file)

# Start the Tkinter main loop
root.mainloop()
