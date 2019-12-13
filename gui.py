# Provides a GUI layer to the Fancy Formats logic module

import ctypes
import logic
import tkinter as tk

from sys import exc_info
from tkinter import filedialog

format_options = ['"Odds & Evens"']


def file_select():
    # Have the user select the results xml file.
    xml_path = filedialog.askopenfilename(
        title="Select SI Timing XML results file",
        filetypes=(("xml files", "*.xml"), ("all files", "*.*"))
    )
    return xml_path


class GUI(tk.Frame):
    # TODO display any error messages in a GUI window.
    # ctypes.windll.user32.MessageBoxW(
    #     0, 'Error: {}\nPlease try again.'.format(e))
    def __init__(self, master: tk.Tk, results_xml):
        super().__init__(master)
        self.master = master
        event_title = logic.get_title(results_xml)

        self.master.title(event_title)
        tk.Label(self, text=event_title).grid(row=0, column=0, columnspan=2)

        # Drop-down box for the user to select the course to be processed.
        course_selected = tk.StringVar()
        course_options = logic.list_courses(results_xml)
        course_menu = tk.OptionMenu(self, course_selected, *course_options)
        course_menu.grid(row=1, column=1)
        tk.Label(self, text='Select a course:  ').grid(row=1, column=0)

        # Drop-down box for the user to select the format against which the
        # course will be processed.
        format_selected = tk.StringVar()
        self.format_widgets = []
        self.format_widgets.append(tk.OptionMenu(self,
                                                 format_selected,
                                                 *logic.format_options))
        self.format_widgets[0].grid(row=2, column=1)
        self.format_widgets.append(tk.Label(self, text='Select a format:  '))
        self.format_widgets[1].grid(row=2, column=0)
        for widget in self.format_widgets:
            widget.grid_remove()

        def course_change(*args):
            course_selected_val = course_selected.get()
            if course_selected_val in course_options:
                course_index = course_options.index(course_selected_val)
                self.course_xml = logic.get_course(results_xml, course_index)
                # self.create_format_menu()
                for widget in self.format_widgets:
                    widget.grid()

        course_selected.trace('w', course_change)

        # TODO will need to set self.course_xml for re-use throughout GUI.

        self.pack()


if __name__ == '__main__':
    tk_root = tk.Tk()
    # Hide the main tk window.
    tk_root.iconify()

    results_xml = None
    # Have the user select the results xml file.
    xml_path = file_select()
    if xml_path:
        # Attempt to process the selected xml file.
        try:
            results_xml = logic.import_xml(xml_path)
        except Exception:
            ctypes.windll.user32.MessageBoxW(
                0, 'Error processing XML file', 'Error', 0)

    if results_xml:
        # Show the main tk window and initialise the GUI.
        tk_root.deiconify()
        ff_gui = GUI(tk_root, results_xml)
        tk_root.mainloop()
