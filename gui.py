# Provides a GUI layer to the Fancy Formats logic module

import logic
import tkinter as tk

from tkinter import filedialog


class GUI(tk.Frame):
    def __init__(self, master, results_xml):
        super().__init__(master)

        # TODO have a title somewhere with the Name from the Event xml tree.

        # Drop-down box for the user to select the course to be processed.
        course_selected = tk.StringVar(master)
        course_options = logic.list_courses(results_xml)
        course_menu = tk.OptionMenu(self, course_selected, *course_options)
        course_menu.grid(row=0, column=1)
        tk.Label(self, text='Select a course:  ').grid(row=0, column=0)

        # TODO will need to set self.course_xml for re-use throughout GUI.

        self.pack()


if __name__ == '__main__':
    tk_root = tk.Tk()
    # Hide the main tk window.
    tk_root.iconify()

    # Have the user select the results xml file.
    xml_path = filedialog.askopenfilename(
            filetypes=(("xml files", "*.xml"), ("all files", "*.*"))
    )
    # Attempt to process the selected xml file.
    results_xml = logic.import_xml(xml_path)
    # TODO display any error messages in a GUI window.

    # Show the main tk window and initialise the GUI.
    tk_root.deiconify()
    ff_gui = GUI(tk_root, results_xml)
    tk_root.mainloop()
