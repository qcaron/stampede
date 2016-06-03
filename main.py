# -*- coding: utf-8 -*-

import subprocess
import os
import platform
import configparser
import io
from PyPDF2 import PdfFileWriter, PdfFileReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from tkinter import Tk, Frame, Button, Label, Entry, Menu, filedialog, StringVar, simpledialog
from tkinter import BOTTOM, TOP, RIGHT, LEFT, BOTH, X, DISABLED, NORMAL

IMAGE_DENSITY = 250


class Stamp(object):
    """
    Build a stamp according to base info
    """
    SERIES_ZFILL = 4
    INDEX_ZFILL = 4

    def __init__(self, case, team, series, last_index):
        self.case = case
        self.team = team
        self.series = int(series)
        self.last_index = int(last_index)
        self.next_index = self.last_index
        self.str_stamp = "null"

    def increase_series(self):
        self.series += 1

    def _get_next_stamp(self):
        if self.next_index < 9998:
            self.next_index += 1
        else:
            self.next_index = 0
            self.series += 1

        self.str_stamp = "-".join([
            self.case,
            self.team,
            str(self.series).zfill(Stamp.SERIES_ZFILL),
            str(self.next_index).zfill(Stamp.INDEX_ZFILL)
        ])

    def get_next_stamp(self):
        self._get_next_stamp()
        return self.str_stamp


class SettingsDialog(simpledialog.Dialog):
    def __init__(self, *args, **kwargs):
        self.config = kwargs.pop("config")
        self.config_file_name = kwargs.pop("config_file_name")
        super(SettingsDialog, self).__init__(*args, **kwargs)

    def body(self, master):
        Label(master, text="Team").grid(row=0)
        Label(master, text="Case").grid(row=1)

        # self.case_entry = Entry(master, textvariable=self.case).grid(row=0, column=1)
        # self.case_entry = Entry(master, textvariable=self.case).grid(row=1, column=1)
        self.case_entry = Entry(master)
        self.case_entry.grid(row=0, column=1)
        try:
            self.case_entry.insert(0, self.config.get("DEFAULT", "case"))
        except configparser.NoOptionError:
            self.case_entry.insert(0, "CASE")
        self.team_entry = Entry(master)
        self.team_entry.grid(row=1, column=1)
        try:
            self.team_entry.insert(0, self.config.get("DEFAULT", "team"))
        except configparser.NoOptionError:
            self.team_entry.insert(0, "TEAM")

        return self.case_entry  # Focus

    def apply(self):
        self.config.set("DEFAULT", "case", self.case_entry.get())
        self.config.set("DEFAULT", "team", self.team_entry.get())
        with open(self.config_file_name, 'w') as configfile:
            self.config.write(configfile)


class WindowApp(object):
    """
    The PDF Stampede app window
    """
    def __init__(self, resizable=(True, True), geometry=(620, 220)):
        assert (isinstance(resizable, (tuple, list)))
        assert (isinstance(geometry, (tuple, list)))

        self.root = Tk()

        self.config = configparser.ConfigParser()
        self.config_file_name = "config.ini"
        self.config.read(self.config_file_name)

        self.default_case = StringVar(value=self.config["DEFAULT"].get("case", "CASE"))
        self.default_team = StringVar(value=self.config["DEFAULT"].get("team", "TEAM"))
        self.default_series = StringVar()
        self.default_last_index = StringVar()

        self.root.title("The Stampede")
        self.root.resizable(width=resizable[0], height=resizable[1])
        self.root.geometry('{}x{}'.format(geometry[0], geometry[1]))
        self.root.minsize(geometry[0], geometry[1])
        self.root.maxsize(geometry[0]+200, geometry[1])
        self.file_name = StringVar()
        self.file_name.trace("w", self.file_name_changed)
        self.stamp_button = None
        self.add_widgets()
        self.add_menus()
        self.center(self.root)

    def add_widgets(self):
        # File
        frame = Frame(self.root)
        frame.pack(side=TOP, fill=X, expand=True, ipady=5)
        file_label = Label(frame, text="PDF File", width=10)
        file_label.pack(side=LEFT, padx=5, pady=5)
        file_entry = Entry(frame, state=DISABLED, textvariable=self.file_name)
        file_entry.pack(padx=5, side=LEFT, fill=X, expand=True)
        file_button = Button(frame, text="Browse...", command=self.choose_pdf)
        file_button.pack(padx=5, side=RIGHT)

        # Case
        frame = Frame(self.root)
        frame.pack(side=TOP, fill=X, expand=True)
        case_label = Label(frame, text="Case", width=10)
        case_label.pack(side=LEFT, padx=5, pady=5)
        case_entry = Entry(frame, textvariable=self.default_case)
        case_entry.pack(fill=X, padx=5, expand=True)

        # Team
        frame = Frame(self.root)
        frame.pack(fill=BOTH, expand=True)
        team_label = Label(frame, text="Team", width=10)
        team_label.pack(side=LEFT, padx=5, pady=5)
        team_entry = Entry(frame, textvariable=self.default_team)
        team_entry.pack(fill=X, padx=5, expand=True)

        # Series
        frame = Frame(self.root)
        frame.pack(fill=BOTH, expand=True)
        series_label = Label(frame, text="Series", width=10)
        series_label.pack(side=LEFT, padx=5, pady=5)
        series_entry = Entry(frame, textvariable=self.default_series)
        series_entry.pack(fill=X, padx=5, expand=True)

        # Last index
        frame = Frame(self.root)
        frame.pack(fill=BOTH, expand=True)
        last_index_label = Label(frame, text="Last index", width=10)
        last_index_label.pack(side=LEFT, padx=5, pady=5)
        last_index_entry = Entry(frame, textvariable=self.default_last_index)
        last_index_entry.pack(fill=X, padx=5, expand=True)

        bottom_frame = Frame(self.root)
        bottom_frame.pack(side=BOTTOM, fill=X, ipady=5, padx=5)

        close_button = Button(bottom_frame, text="Quit", command=self.root.quit)
        close_button.pack(side=RIGHT)
        self.stamp_button = Button(bottom_frame, text="Stamp it!", state=DISABLED, command=self.stamp_it)
        self.stamp_button.pack(side=RIGHT)

    def stamp_it(self):
        stamp_it(
            self.file_name.get(),
            self.default_case.get(),
            self.default_team.get(),
            self.default_series.get(),
            self.default_last_index.get(),
        )

    def add_menus(self):
        menu_bar = Menu(self.root)
        stampede_menu = Menu(menu_bar, tearoff=0)
        stampede_menu.add_command(label="Settings", command=self.edit_default_settings)
        stampede_menu.add_separator()
        stampede_menu.add_command(label="Quit", command=self.root.quit)
        menu_bar.add_cascade(label="Stampede", menu=stampede_menu)

        self.root.config(menu=menu_bar)

    def run(self):
        self.root.mainloop()

    def center(self, window):
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    def edit_default_settings(self):
        SettingsDialog(self.root, config=self.config, config_file_name=self.config_file_name)

    def choose_pdf(self):
        self.file_name.set(filedialog.askopenfilename(filetypes=(("PDF files", "*.pdf"),)))

    def file_name_changed(self, *args):
        if self.file_name.get():
            self.stamp_button.configure(state=NORMAL)
        else:
            self.stamp_button.configure(state=DISABLED)


def stamp_it(selected_path, stamp_case, stamp_team, stamp_series, stamp_last_index):
    # TODO Fix bin path for other system use, especially Windows
    # selected_path = "./test/Circulaire du 16-11-2012.pdf"

    # File info
    file_dirname = os.path.dirname(selected_path)
    file_basename = os.path.basename(selected_path)
    file_name, file_extension = os.path.splitext(file_basename)

    # Make sure the selected file is a PDF
    if file_extension not in (".pdf", ):
        raise ValueError("The document must be a PDF (either .pdf or .PDF)")

    stamp = Stamp(stamp_case, stamp_team, stamp_series, stamp_last_index)

    # Add image magick binaries to the environment PATH
    os.environ["PATH"] += ":/usr/local/bin"

    operating_system = platform.system()
    architecture = platform.architecture()

    if operating_system in ("Linux", "Linux2"):
        pass
    elif operating_system == "Darwin":
        if architecture[0] == "64bit":
            os.environ["PATH"] += ":{}".format(os.path.join(os.getcwd(), "xpdfbin-mac-3.04/bin64"))
    elif operating_system == "Win32":
        pass

    # Start processing the PDF file
    print("Creating images from PDF pages...")

    stamped_pdf = PdfFileWriter()
    stamps = [stamp.get_next_stamp()]

    with open(selected_path, "rb") as existing_pdf_file:
        existing_pdf = PdfFileReader(existing_pdf_file)
        # Get text content
        num_pages = existing_pdf.numPages
        output_pdf_file_path = os.path.join(file_dirname, "{}.pdf".format(stamps[-1]))

        completed_process = subprocess.run(
            [
                "pdftotext",
                "-enc",
                "UTF-8",
                selected_path,
                os.path.join(file_dirname, "{}.txt".format(stamps[-1])),
            ]
        )

        if completed_process.returncode == 0:
            print("{} page(s) to stamp".format(num_pages))
        else:
            print("An error occured: \n{}\n".format(completed_process.stderr))

        # Create stamped PDF
        with open(output_pdf_file_path, "wb") as output_pdf_file:
            for page_index in range(num_pages):
                print("Stamping page {}".format(page_index+1))

                canvas_io = io.BytesIO()

                # create a new PDF with Reportlab
                can = canvas.Canvas(canvas_io, pagesize=A4)
                can.drawString(475, 5, stamps[-1])
                can.save()

                # move to the beginning of the StringIO buffer
                canvas_io.seek(0)

                new_pdf = PdfFileReader(canvas_io)

                page = existing_pdf.getPage(page_index)
                watermarked_page = new_pdf.getPage(0)
                page.mergePage(watermarked_page)
                stamped_pdf.addPage(page)

                # Get next stamp
                stamps.append(stamp.get_next_stamp())

            # finally, write "output" to a real file
            stamped_pdf.write(output_pdf_file)

    # Save pages as stamped TIFF images
    print("Will now stamp files and save pages as TIFF...")

    for page_index in range(num_pages):
        completed_process = subprocess.run(
            [
                "convert",
                "-density",
                str(IMAGE_DENSITY),
                "-alpha",
                "off",
                output_pdf_file_path + "[{}]".format(page_index),
                os.path.join(file_dirname, "{}.tiff".format(stamps[page_index]))
            ]
        )

        if completed_process.returncode == 0:
            continue
        else:
            print("An error occured for page {}: \n{}\n".format(page_index + 1, completed_process.stderr))

if __name__ == "__main__":
    window = WindowApp()
    window.run()
