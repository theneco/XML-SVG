# gui_main.py

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
import os

# Import the conversion function from our other file
# Ensure converter_logic.py is in the same directory
from converter_logic import convert_xml_to_svg

class App(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("XML to SVG Converter")
        self.geometry("500x600")
        self.minsize(450, 500)

        # --- State Variables ---
        self.file_paths = set()  # Use a set to automatically handle duplicates
        self.output_folder_path = tk.StringVar(value="No output folder selected")

        # --- Styling ---
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.configure(background='#eaf2f8')
        self.style.configure('TButton', padding=6, relief='flat', font=('Segoe UI', 10, 'bold'))
        self.style.configure('TLabel', background='#eaf2f8', font=('Segoe UI', 10))
        self.style.configure('TFrame', background='#eaf2f8')

        # --- Main Layout ---
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(expand=True, fill="both")
        
        self.create_drop_zone(main_frame)
        self.create_file_list(main_frame)
        self.create_output_widgets(main_frame)
        self.create_action_buttons(main_frame)
        self.create_status_bar()

    def create_drop_zone(self, parent):
        """Creates the dotted area for dropping files."""
        drop_frame = ttk.Frame(parent, relief="sunken", style='TFrame')
        drop_frame.pack(fill="x", pady=5)
        
        drop_label = ttk.Label(
            drop_frame,
            text="Drag & Drop XML Files Here",
            font=("Segoe UI", 12, "italic"),
            anchor="center",
            padding=20,
            style="TLabel"
        )
        drop_label.pack(expand=True, fill="both")

        # Register the label itself for drag-and-drop
        drop_label.drop_target_register(DND_FILES)
        drop_label.dnd_bind('<<Drop>>', self.handle_drop)

    def create_file_list(self, parent):
        """Creates the listbox to show staged files."""
        list_frame = ttk.Frame(parent)
        list_frame.pack(expand=True, fill="both", pady=5)
        
        list_label = ttk.Label(list_frame, text="Files to Convert:")
        list_label.pack(anchor="w")

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.file_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            bg="#ffffff",
            font=("Segoe UI", 10),
            selectmode=tk.SINGLE
        )
        self.file_listbox.pack(expand=True, fill="both")
        scrollbar.config(command=self.file_listbox.yview)

    def create_output_widgets(self, parent):
        """Creates widgets for selecting the output folder."""
        output_frame = ttk.Frame(parent)
        output_frame.pack(fill="x", pady=(10, 5))

        select_folder_btn = ttk.Button(
            output_frame,
            text="Select Output Folder",
            command=self.select_folder
        )
        select_folder_btn.pack(side="left")

        folder_label = ttk.Label(
            output_frame,
            textvariable=self.output_folder_path,
            font=("Segoe UI", 9, "italic"),
            wraplength=300,
            anchor="w"
        )
        folder_label.pack(side="left", padx=10, fill="x", expand=True)

    def create_action_buttons(self, parent):
        """Creates the main action buttons (Convert, Clear)."""
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill="x", pady=10)

        self.clear_btn = ttk.Button(
            action_frame,
            text="Clear List",
            command=self.clear_list
        )
        self.clear_btn.pack(side="left", expand=True, fill="x", padx=(0, 5))
        
        self.convert_btn = ttk.Button(
            action_frame,
            text="Convert Files",
            command=self.start_conversion,
            state="disabled"
        )
        self.convert_btn.pack(side="left", expand=True, fill="x", padx=(5, 0))

    def create_status_bar(self):
        """Creates the status bar at the bottom."""
        self.status_label = ttk.Label(self, text="Ready", relief="sunken", anchor="w", padding=5)
        self.status_label.pack(side="bottom", fill="x")

    def handle_drop(self, event):
        """Handles dropped files, adding them to the list."""
        filepaths = self.tk.splitlist(event.data)
        added_count = 0
        for path in filepaths:
            if path.lower().endswith('.xml') and path not in self.file_paths:
                self.file_paths.add(path)
                self.file_listbox.insert(tk.END, os.path.basename(path))
                added_count += 1
        if added_count > 0:
            self.status_label.config(text=f"Added {added_count} new file(s).")
            self.check_button_state()
    
    def select_folder(self):
        """Opens a dialog to select the output folder."""
        folder_selected = filedialog.askdirectory(title="Select Output Folder")
        if folder_selected:
            self.output_folder_path.set(folder_selected)
            self.status_label.config(text=f"Output folder set.")
            self.check_button_state()

    def check_button_state(self):
        """Enables or disables the Convert button based on state."""
        if self.file_paths and os.path.isdir(self.output_folder_path.get()):
            self.convert_btn.config(state="normal")
        else:
            self.convert_btn.config(state="disabled")

    def clear_list(self):
        """Clears the file list and resets state."""
        self.file_paths.clear()
        self.file_listbox.delete(0, tk.END)
        self.status_label.config(text="File list cleared.")
        self.check_button_state()

    def start_conversion(self):
        """The main batch conversion process."""
        output_folder = self.output_folder_path.get()
        files_to_convert = list(self.file_paths)
        total_files = len(files_to_convert)

        success_count = 0
        error_list = []

        for i, input_path in enumerate(files_to_convert):
            base_name = os.path.basename(input_path)
            self.status_label.config(text=f"Processing {i + 1}/{total_files}: {base_name}")
            self.update_idletasks()

            try:
                output_filename = os.path.splitext(base_name)[0] + '.svg'
                output_path = os.path.join(output_folder, output_filename)
                convert_xml_to_svg(input_path, output_path)
                success_count += 1
            except Exception as e:
                error_list.append(f"{base_name}: {e}")

        summary_message = f"Successfully converted {success_count} of {total_files} files."
        if error_list:
            summary_message += "\n\nErrors:\n- " + "\n- ".join(error_list)
            messagebox.showwarning("Batch Complete with Errors", summary_message)
        else:
            messagebox.showinfo("Batch Complete", summary_message)
            
        self.status_label.config(text="Conversion complete. Ready.")


if __name__ == "__main__":
    app = App()
    app.mainloop()