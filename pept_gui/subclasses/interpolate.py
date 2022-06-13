from PyQt5.QtWidgets import (
    QApplication, QDialog, QMainWindow, QMessageBox, QFileDialog, QLabel,QTextEdit
)
import pept
import pept.tracking as tracking
import time
from PyQt5.uic import loadUi

class Interpolate(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        loadUi("ui/interpolate.ui", self)
        self.ok_button.clicked.connect(self.ok_button_clicked)
        self.cancel_button.clicked.connect(self.cancel_button_clicked)
        self.timestep.setText("1")

    def ok_button_clicked(self):
        print("OK button clicked")
        timestep = float(self.timestep.toPlainText())
        time_ = time.time()
        self.parent.pept_pipeline[f"Interpolate_{time_}"] = {"function": tracking.Interpolate,"name": "tracking.Interpolate", "kwargs": {"timestep": timestep,},"update": True, "skip": False}
        self.parent.pipeline_execution_order.append(f"Interpolate_{time_}")
        self.parent.module_list.addItem(f"Interpolate_{time_}")
        self.parent.plot_item = f"Interpolate_{time_}"
        self.close()

    def cancel_button_clicked(self):
        print("Cancel button clicked")
        self.close()
