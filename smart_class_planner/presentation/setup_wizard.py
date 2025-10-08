import tkinter as tk
from tkinter import filedialog, messagebox

class SetupWizard:
    """Tkinter-based GUI for Smart Class Planning Tool."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Smart Class Planning Tool")

    def run(self):
        tk.Label(self.root, text="Upload DegreeWorks PDF").pack(pady=5)
        tk.Button(self.root, text="Browse", command=self.upload_pdf).pack(pady=5)
        tk.Button(self.root, text="Generate Plan", command=self.generate_plan).pack(pady=10)
        self.root.mainloop()

    def upload_pdf(self):
        file = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        messagebox.showinfo("File Uploaded", f"Loaded: {file}")

    def generate_plan(self):
        messagebox.showinfo("Plan Generation", "Coming soon...")
