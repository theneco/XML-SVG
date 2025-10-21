# gui_main.py

import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
import os

# Import the conversion function from our other file
from converter_logic import convert_xml_to_svg

class App(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("XML to SVG Converter")
        self.geometry("400x250")

        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.handle_drop)

        self.main_label = tk.Label(
            self,
            text="Drag and drop an XML file here",
            pady=40,
            font=("Helvetica", 14)
        )
        self.main_label.pack(expand=True, fill="both")

        self.status_label = tk.Label(self, text="Waiting for file...", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def handle_drop(self, event):
        # This is where we'll process the file
        filepath = event.data.strip('{}') # Clean up the path string from the event
        self.process_file(filepath)

    def process_file(self, input_path):
        self.status_label.config(text=f"Received: {os.path.basename(input_path)}")
            # 1. Input Sanitization
        if not input_path.lower().endswith('.xml'):
            messagebox.showerror("Error", "Invalid file type. Please drop a valid .xml file.")
            self.status_label.config(text="Error: Not an XML file. Waiting for file...")
            return

        # 2. "Save As" Dialog
        initial_filename = os.path.splitext(os.path.basename(input_path))[0] + '.svg'
        output_path = filedialog.asksaveasfilename(
            initialfile=initial_filename,
            defaultextension=".svg",
            filetypes=[("Scalable Vector Graphics", "*.svg"), ("All Files", "*.*")]
        )

        if not output_path: # User cancelled the save dialog
            self.status_label.config(text="Save cancelled. Waiting for file...")
            return

        # 3. Call conversion logic with error handling
        try:
            convert_xml_to_svg(input_path, output_path)
            self.status_label.config(text=f"Success! Saved to {os.path.basename(output_path)}")
            messagebox.showinfo("Success", f"File converted successfully and saved to:\n{output_path}")
        except Exception as e:
            self.status_label.config(text=f"Error during conversion: {e}")
            messagebox.showerror("Conversion Error", f"An error occurred:\n{e}")


if __name__ == "__main__":
    app = App()
    app.mainloop()