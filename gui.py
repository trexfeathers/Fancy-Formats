# Provides a GUI layer to the Fancy Formats logic module

import ctypes
import logic
import tkinter as tk
from os import path

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
        self.event = event
        event_name = event.event_name

        self.master.title(event_name)
        tk.Label(self, text=event_name).grid(row=0, column=0, columnspan=2)

        # Drop-down box for the user to select the course to be processed.
        self.course_selected = tk.StringVar()
        self.course_options = event.list_courses()
        self.course_widgets = [
            tk.Label(self, text='Select a course:  '),
            tk.OptionMenu(self, self.course_selected, *self.course_options)
        ]
        for ix, widget in enumerate(self.course_widgets):
            widget.grid(row=1, column=ix, sticky='W')

        # Drop-down box for the user to select the format against which the
        # course will be processed.
        self.format_selected = tk.StringVar()
        self.format_widgets = [
            tk.Label(self, text='Select a format:  '),
            tk.OptionMenu(self, self.format_selected, []),
        ]
        self.menu_format_options = self.format_widgets[1]
        for ix, widget in enumerate(self.format_widgets):
            widget.grid(row=2, column=ix, sticky='W')
            widget.grid_remove()

        self.course_selected.trace('w', self.course_change)
        self.format_selected.trace('w', self.format_change)

        self.input_widgets = []

        self.grid()

    def course_change(self, *args):
        course_selected_val = self.course_selected.get()
        if course_selected_val in self.course_options:
            course_index = self.course_options.index(course_selected_val)
            self.course = self.event.course_list[course_index]
            # self.create_format_menu()

            self.format_selected.set('')
            menu = self.menu_format_options["menu"]
            menu.delete(0, "end")
            for format in self.course.format_options:
                menu.add_command(
                    label=format,
                    command=lambda
                    value=format: self.format_selected.set(value))

            for widget in self.format_widgets:
                widget.grid()

    def format_change(self, *args):
        for widget in self.input_widgets:
            widget.grid_forget()

        try:
            format_selected_func = \
                self.course.format_options[self.format_selected.get()]
        except KeyError:
            format_selected_func = None

        if format_selected_func == self.course.evaluate_odds_evens:
            first_column = self.grid_size()[0]
            self.input_widgets = [
                tk.Label(self, text='Set file name: '),
                tk.Label(self, text='Select penalty format: '),
                tk.Label(self, text='Set penalty per control: ')
            ]

            for ix, widget in enumerate(self.input_widgets):
                widget.grid(column=first_column, row=ix + 1, padx=(20, 5),
                            sticky='W')

            penalty_format = tk.StringVar()
            widget_output_path = tk.Text(self, height=1, width=30)
            widget_penalty_format = tk.OptionMenu(self, penalty_format,
                                                  'points', 'seconds')
            widget_penalty_per = tk.Text(self, height=1, width=10)

            for ix, widget in enumerate((widget_output_path,
                                         widget_penalty_format,
                                         widget_penalty_per)):
                widget.grid(column=first_column + 1, row=ix + 1, pady=5,
                            sticky='W')
                self.input_widgets.append(widget)

            output_dir = path.dirname(xml_path)
            go_button = tk.Button(
                self,
                text='GO',
                width=20,
                command=lambda: format_selected_func(path.join(output_dir,widget_output_path.get(1.0, tk.END)),
                                     penalty_format.get(),
                                     int(widget_penalty_per.get(1.0, tk.END))))
            go_button.grid(column=first_column, row=4, columnspan=2, pady=5)

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
