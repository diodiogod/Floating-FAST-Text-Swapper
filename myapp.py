import tkinter as tk
from tkinterdnd2 import TkinterDnD, DND_FILES
import os
import re

os.environ['TKDND_LIBRARY'] = os.path.join(os.path.dirname(__file__), 'tkdnd2.9.2')


# Function to replace words and preserve case
def replace_word(content, old_word, new_word, swap_mode=False):
    def replace_case(word, replacement_word):
        if word.isupper():
            # If the whole word is uppercase, keep replacement uppercase
            return replacement_word.upper()
        elif word[0].isupper():
            # If only the first letter is uppercase, capitalize the replacement
            return replacement_word.capitalize()
        else:
            # Otherwise, make the replacement lowercase
            return replacement_word.lower()

    # Split content into words and process each word individually
    words = re.split(r'(\W+)', content)  # Split by non-word characters to preserve spaces and punctuation

    for i, word in enumerate(words):
        if swap_mode:
            # Swap both ways without looping
            if re.fullmatch(old_word, word, re.IGNORECASE):
                words[i] = replace_case(word, new_word)
            elif re.fullmatch(new_word, word, re.IGNORECASE):
                words[i] = replace_case(word, old_word)
        else:
            # Standard replacement from old_word to new_word
            if re.fullmatch(old_word, word, re.IGNORECASE):
                words[i] = replace_case(word, new_word)

    return ''.join(words)  # Join the list back into a string

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
        modified_content = replace_word(content, old_word, new_word, swap_mode=swap_mode)

        # Save the file automatically
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(modified_content)

        label_status.config(text=f"File processed: {os.path.basename(filepath)}")

# Create a floating, draggable window with tkinter
root = TkinterDnD.Tk()  # Use TkinterDnD for drag-and-drop
root.title("Text Replacer")
root.geometry("400x250")
root.wm_attributes("-topmost", 1)  # Keep the window on top

# Add labels and entry fields for input
label_find = tk.Label(root, text="Word to find:")
label_find.pack(pady=5)
entry_find = tk.Entry(root)
entry_find.pack(pady=5)

label_replace = tk.Label(root, text="Word to replace with:")
label_replace.pack(pady=5)
entry_replace = tk.Entry(root)
entry_replace.pack(pady=5)

# Add a checkbox for swap mode
swap_var = tk.IntVar()
check_swap = tk.Checkbutton(root, text="Swap mode (two-way replace)", variable=swap_var)
check_swap.pack(pady=5)

label_status = tk.Label(root, text="Drop a .txt file here")
label_status.pack(pady=20)

# Enable the window to accept drag-and-drop of files
root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', handle_file)

# Start the Tkinter main loop
root.mainloop()
