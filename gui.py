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
    def __init__(self, master: tk.Tk, event: logic.IofEvent):
        super().__init__(master)
        self.master = master
        event_name = event.event_name

        self.master.title(event_name)
        tk.Label(self, text=event_name).grid(row=0, column=0, columnspan=2)

        # Drop-down box for the user to select the course to be processed.
        course_selected = tk.StringVar()
        course_options = event.list_courses()
        self.course_widgets = [
            tk.Label(self, text='Select a course:  '),
            tk.OptionMenu(self, course_selected, *course_options)
        ]
        for ix, widget in enumerate(self.course_widgets):
            widget.grid(row=1, column=ix)

        # Drop-down box for the user to select the format against which the
        # course will be processed.
        format_selected = tk.StringVar()
        self.format_widgets = [
            tk.Label(self, text='Select a format:  '),
            tk.OptionMenu(self, format_selected, []),
        ]
        self.menu_format_options = self.format_widgets[1]
        for ix, widget in enumerate(self.format_widgets):
            widget.grid(row=2, column=ix)
            widget.grid_remove()

        def course_change(*args):
            course_selected_val = course_selected.get()
            if course_selected_val in course_options:
                course_index = course_options.index(course_selected_val)
                course = event.course_list[course_index]
                # self.create_format_menu()

                format_selected.set('')
                menu = self.menu_format_options["menu"]
                menu.delete(0, "end")
                for format in course.format_options:
                    menu.add_command(
                        label=format,
                        command=lambda
                        value=format: format_selected.set(value))

                for widget in self.format_widgets:
                    widget.grid()

        course_selected.trace('w', course_change)

        self.pack()


if __name__ == '__main__':
    tk_root = tk.Tk()
    # Hide the main tk window.
    tk_root.iconify()

    results_xml = None
    # Have the user select the results xml file.
    xml_path = file_select()
    if xml_path:
        event = logic.IofEvent(xml_path)
        if event:
            # Show the main tk window and initialise the GUI.
            tk_root.deiconify()
            ff_gui = GUI(tk_root, event)
            tk_root.mainloop()
