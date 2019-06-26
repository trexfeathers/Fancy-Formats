import process_results
import tkinter as tk

from tkinter import filedialog


class gui(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.xml_path = filedialog.askopenfilename(
            filetypes=(("xml files", "*.xml"), ("all files", "*.*"))
        )

        process_results.import_xml(self.xml_path)


if __name__ == '__main__':
    tk_root = tk.Tk()
    ff_gui = gui(tk_root)