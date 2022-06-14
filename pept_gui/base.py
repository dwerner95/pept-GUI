"""
pept_gui base module.

This is the principal module of the pept_gui project.
here you put your main classes and objects.

Be creative! do whatever you want!

If you want to replace this with a Flask application run:

    $ make init

and then choose `flask` as template.
"""

# example constant variable
NAME = "pept_gui"
import sys
from tkinter import dialog
import plotly
import time
import pept
import pept.tracking as tracking
from plotly.graph_objects import Figure, Scatter
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QDialog, QMainWindow, QMessageBox, QFileDialog, QLabel,QTextEdit, QCheckBox
)
from PyQt5.uic import loadUi
from PyQt5 import QtCore

# own modules
from .main_ui import Ui_MainWindow
from .pept_editor_ui import Ui_Dialog
from .subclasses.peptml import PeptMl
from .subclasses.birmingham import Birmingham
from .subclasses.cutpoints import Cutpoints
from .subclasses.condition import Condition
from .subclasses.segregate import Segregate
from .subclasses.interpolate import Interpolate


class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.custom_setup()
        self.connectSignalsSlots()
        self.pept_pipeline ={}
        self.pipeline_header={}
        self.pipeline_execution_order = []
        self.old_data={}
        self.sample_size = None
        self.overlap = None
        self.time = None
        self.time_step = None
        self.lors = None
        self.plot_item = None
        self.update_button_clicked()
        self.UpdateButton.setEnabled(False)
        #  check if commanline arg was given as filename
        if len(sys.argv) > 1:
            self.load_file(sys.argv[1])


    def custom_setup(self):
        self.UpdateButton.clicked.connect(self.update_button_clicked)
        self.textBrowser.setText("Hello World")
        self.TimeSelector.setMinimum(0)
        self.TimeSelector.setMaximum(1000)
        self.TimeSizeSelector.setMinimum(1)
        self.TimeSizeSelector.setMaximum(1000)

    def update_button_clicked(self):
        print("Update button clicked")
        # read in boxes
        if self.time != self.TimeSelector.value() or self.time_step != self.TimeSizeSelector.value():
            self.time = self.TimeSelector.value()
            self.time_step = self.TimeSizeSelector.value()
            self.update_pipeline = True
        # check if sample size and overlap have been changed. if so update them and set first element in pipeline to update
        if self.sample_size != float(self.SampleSize.toPlainText()) or self.overlap != float(self.Overlap.toPlainText()):
            self.sample_size=float(self.SampleSize.toPlainText())
            self.overlap = float(self.Overlap.toPlainText())
            self.update_pipeline = True
        self.maxtracer = float(self.MaxTracer.toPlainText())
        # update the lor instance if it exists
        if self.lors is not None:
            try:
                self.lors.sample_size = int( self.sample_size)
                self.lors.overlap = int(self.overlap)
            except ValueError as e:
                try:
                    self.lors.overlap = int(self.overlap)
                    self.lors.sample_size = int( self.sample_size)
                except ValueError as e:
                    QMessageBox.warning(self, "Error", f"{e}")
            # Plot the lors
            self.time_idx = int(self.time/1000 * len(self.lors))
            self.samples_to_plot = int(self.time_step/1000 * len(self.lors))
            # main plotting function
            self.plot()


    def connectSignalsSlots(self):
        self.actionCutpoints.triggered.connect(self.cutpoints)
        self.actionPeptML.triggered.connect(self.peptml)
        self.actionBirmingham_Method.triggered.connect(self.birmingham)
        self.actionCondition.triggered.connect(self.condition)
        self.actionSegregate.triggered.connect(self.segregate)
        self.actionInterpolate.triggered.connect(self.interpolate)
        self.action_export.triggered.connect(self.export)
        self.Load.triggered.connect(self.load_file)
        self.module_list.itemDoubleClicked.connect(self.module_list_item_doubleclicked)
        self.module_list.itemClicked.connect(self.module_list_item_clicked)
        pass
        #self.action_Exit.triggered.connect(self.close)
        #self.action_Find_Replace.triggered.connect(self.findAndReplace)
        #self.action_About.triggered.connect(self.about)


    def peptml(self):
        print("PeptML")
        dialog = PeptMl(self)
        dialog.exec()
        self.print_dict()

    def birmingham(self):
        print("Birmingham")
        dialog = Birmingham(self)
        dialog.exec()
        self.print_dict()

    def cutpoints(self):
        print("Cutpoints")
        dialog = Cutpoints(self)
        dialog.exec()
        self.print_dict()

    def condition(self):
        print("Condition")
        dialog = Condition(self)
        dialog.exec()
        self.print_dict()

    def segregate(self):
        print("Segregate")
        dialog = Segregate(self)
        dialog.exec()
        self.print_dict()

    def interpolate(self):
        print("Interpolate")
        dialog = Interpolate(self)
        dialog.exec()
        self.print_dict()

    def export(self):
        print("Export")
        file_name = QFileDialog.getSaveFileName(self, "Save File", "", "Text Files (*.py)")
        if file_name[0] != "":
            with open(file_name[0], "w") as f:
                f.write("import pept\n")
                f.write("import numpy as np\n")
                f.write("import pept.tracking as tracking\n")
                # write pipeline header dict to file
                function = self.pipeline_header["f"]
                kwargs = self.pipeline_header["kwargs"]
                f.write(f"lors = {function}(*{kwargs})\n")
                f.write(f"lors.sample_size = {int(self.sample_size)}\n")
                f.write(f"lors.overlap = {int(self.overlap)}\n")
                f.write(f"pipeline = pept.Pipeline([\n ")
                for module in self.pipeline_execution_order:
                    if self.pept_pipeline[module]['name'] == "tracking.Condition":
                        f.write(f"    {self.pept_pipeline[module]['name']}('{self.pept_pipeline[module]['kwargs']['cond']}'),\n")
                    else:
                        f.write(f"    {self.pept_pipeline[module]['name']}(**{self.pept_pipeline[module]['kwargs']}),\n")
                f.write("tracking.Stack(),])\n")
                f.write("points = pipeline.fit(lors)\n")
                f.write("# Save points after this!")
            QMessageBox.information(self, "Success", f"Script saved to {file_name[0]}\n Please edit the script to save the positions!")



    def print_dict(self):
        self.textBrowser.setText(f"{self.pept_pipeline}")

    def plot(self):
        plot_2d = self.checkBox_2d.isChecked()
        if self.lors is None:
            return
        if plot_2d:
            if self.plot_item == "lors":
                QMessageBox.warning(self, "Error", "You can not plot LORs in 2D")
            else:
                self.run_to(self.plot_item)
                self.plot_points2d()
        else:
            if self.plot_item == "lors":
                self.plot_lors()
            else:
                self.run_to(self.plot_item)
                self.plot_points3d()

        pass


    def plot_lors(self):
        # Plot the lors
        fig = pept.plots.PlotlyGrapher().add_lines(self.lors[int(self.time_idx)]).fig
        html = '<html><body>'
        html += plotly.offline.plot(fig, output_type='div', include_plotlyjs='cdn')
        html += '</body></html>'
        self.PlotlyPlotRegion.setHtml(html)

    def plot_points2d(self):
        # Plot the lors

        fig = pept.plots.PlotlyGrapher2D().add_timeseries(self.points).fig
        html = '<html><body>'
        html += plotly.offline.plot(fig, output_type='div', include_plotlyjs='cdn')
        html += '</body></html>'
        self.PlotlyPlotRegion.setHtml(html)

    def plot_points3d(self):
        # Plot the lors
        fig = pept.plots.PlotlyGrapher().add_points(self.points).fig
        html = '<html><body>'
        html += plotly.offline.plot(fig, output_type='div', include_plotlyjs='cdn')
        html += '</body></html>'
        self.PlotlyPlotRegion.setHtml(html)

    def load_file(self,filename =None):
        print(filename)
        if type(filename) != str:
            file =QFileDialog.getOpenFileName(self, 'Open file', '')[0]
        else:
            file = filename
        if file.endswith(".da01"):
            # load data with pept.adacforte
            print("Loading Files. This may take a while...")
            self.lors = pept.scanners.adac_forte(
                file,
            )
            self.pipeline_header = {"f": "pept.scanners.adac_forte", "kwargs": {file}}
            self.UpdateButton.setEnabled(True)
        
        if file.endswith(".csv"):
            # load data with pept.csv
            print("Loading Files. This may take a while...")
            self.lors = pept.read_csv(
                file,
            )
            self.pipeline_header = {"f": "pept.read_csv", "kwargs": {file}}
            self.UpdateButton.setEnabled(True)


        else:
            # Rais e a not implemented errror
            raise NotImplementedError("Other file formats not implemented")
        self.num_lors = self.lors.lines.shape[0]
        self.plot_item = "lors"

    def module_list_item_doubleclicked(self, item):
        dialog = PeptEditor(self, item.text())
        dialog.exec()
        self.print_dict()

    def module_list_item_clicked(self, item):
        self.plot_item =  item.text()
        self.print_dict()

    """
    Function run_to(self, item):
    runs the pipeline to the given item
    if there was no update, self.points will be updated to the items previous output
    """
    def run_to(self, item):
        if item not in self.pipeline_execution_order:
            QMessageBox.warning(self, "Error", f"{item} is not in the pipeline")
            return
        data = self.lors[self.time_idx:self.time_idx+self.samples_to_plot]
        # run --> a variable determining if there was an update in the previous pipeline
        update_from_now = False
        for module in self.pipeline_execution_order:
            if self.update_pipeline:
                self.pept_pipeline[module]["update"] = True
            elif self.pept_pipeline[module]["update"] == True and not self.pept_pipeline[module]["skip"] == True:
                update_from_now = True
            else:
                self.pept_pipeline[module]["update"] = update_from_now
        for module in self.pipeline_execution_order:
            print(module)
            print(self.pept_pipeline[module])
            print(self.update_pipeline)
            if self.pept_pipeline[module]["skip"]:
                if module == item:
                    break
                continue
            if self.pept_pipeline[module]["update"] == False:
                data = self.old_data[module]
                if module == item:
                    break
                continue
            func = self.pept_pipeline[module]["function"]
            kwargs = self.pept_pipeline[module]["kwargs"]
            print(func, kwargs)
            data=func(**kwargs).fit(data)
            self.old_data[module] = data
            self.pept_pipeline[module]["update"] = False
            if module == item:
                break

        self.update_pipeline = False
        self.points = data
class PeptEditor(QDialog, Ui_Dialog):
    def __init__(self, parent=None, function=None):
        super().__init__(parent)
        self.parent = parent
        self.setupUi(self)
        self.done.clicked.connect(self.ok_button_clicked)
        self.Cancel.clicked.connect(self.cancel_button_clicked)
        self.delete.clicked.connect(self.delete_button_clicked)
        self.pause.clicked.connect(self.pause_button_clicked)
        if function is not None:
            self.function = function
            kwargs = self.parent.pept_pipeline[function]["kwargs"]
            if self.parent.pept_pipeline[function]["skip"]:
                self.pause.setText("Resume")
            pos = 30
            self.label =[]
            self.textEdit = []
            for id_, data in enumerate(kwargs.items()):
                key, value = data
                self.label.append(QLabel(self.Dialog))
                self.label[-1].setGeometry(QtCore.QRect(60, pos, 90, 31))
                self.label[-1].setObjectName(f"label_{id_}")
                self.label[-1].setText(key)
                if key == "error":
                    self.textEdit.append(QCheckBox(self.Dialog))
                    self.textEdit[-1].setChecked(value)
                else:
                    self.textEdit.append(QTextEdit(self.Dialog))
                    self.textEdit[-1].setText(str(value))
                self.textEdit[-1].setGeometry(QtCore.QRect(180, pos, 141, 31))
                self.textEdit[-1].setObjectName(f"textEdit_{id_}")

                pos +=40

    def ok_button_clicked(self):
        print("Ok button clicked")
        #self.parent.pept_pipeline[self.function]["kwargs"] = {}
        update = False
        for id_, data in enumerate(self.textEdit):
            # check if the new and old one are the same
            print(self.parent.pept_pipeline[self.function]["kwargs"])
            if self.label[id_].text() == "cond":
                if self.parent.pept_pipeline[self.function]["kwargs"][self.label[id_].text()] != data.toPlainText():
                    self.parent.pept_pipeline[self.function]["kwargs"][self.label[id_].text()] = data.toPlainText()
                    update = True
            elif self.label[id_].text() == "error":
                statement=data.isChecked()
                if self.parent.pept_pipeline[self.function]["kwargs"][self.label[id_].text()] != statement:
                    self.parent.pept_pipeline[self.function]["kwargs"][self.label[id_].text()] = statement
                    update = True
            else:
                if self.parent.pept_pipeline[self.function]["kwargs"][self.label[id_].text()] != float(data.toPlainText()):
                    self.parent.pept_pipeline[self.function]["kwargs"][self.label[id_].text()] = float(data.toPlainText())
                    update = True
        if not self.parent.pept_pipeline[self.function]["update"]:
            self.parent.pept_pipeline[self.function]["update"]= update
        # check if the checkboxes are ticked
        if self.checkplot_after.isChecked() and self.checkplot_before.isChecked():
            # message that this is not possible
            QMessageBox.warning(self, "Error", "You cannot plot both before and after the function")
        elif self.checkplot_after.isChecked():
            # find id self.function in the pipeline_execution_order list
            id_ = self.parent.pipeline_execution_order.index(self.function)
            self.parent.plot_item = self.function
        elif self.checkplot_before.isChecked():
            # find id self.function in the pipeline_execution_order list
            id_ = self.parent.pipeline_execution_order.index(self.function)
            if id_ == 0:
                self.parent.plot_item = "lors"

            else:
                self.parent.plot_item = self.parent.pipeline_execution_order[id_-1]
        else:
            # dont change the current plot if it is not wanted

            pass

        self.close()

    def cancel_button_clicked(self):
        print("Cancel button clicked")
        self.close()

    def delete_button_clicked(self):
        print("Delete button clicked")
        self.parent.pept_pipeline.pop(self.function)
        index = self.parent.pipeline_execution_order.index(self.function)
        self.parent.pipeline_execution_order.remove(self.function)

        self.parent.module_list.takeItem(index)
        if self.parent.plot_item == self.function:
            self.parent.plot_item = "lors"
        self.close()

    def pause_button_clicked(self):
        print("Pause button clicked")
        self.parent.pept_pipeline[self.function]["update"]= True
        if self.pause.text() == "Pause":
            self.pause.setText("Resume")
            self.parent.pept_pipeline[self.function]["skip"] = True
            self.parent.update_pipeline = True
        else:
            self.pause.setText("Pause")
            self.parent.pept_pipeline[self.function]["skip"] = False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())
