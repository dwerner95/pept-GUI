from PyQt5.QtWidgets import (
    QApplication, QDialog, QMainWindow, QMessageBox, QFileDialog, QLabel,QTextEdit
)
from PyQt5.QtCore import QUrl
import pept
import pept.tracking as tracking
import time
from PyQt5.uic import loadUi
import os
class PeptMl(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        here = os.path.dirname(os.path.abspath(__file__))
        loadUi(os.path.join(here,"..", "ui","pept_ml.ui"), self)
        self.ok_button.clicked.connect(self.ok_button_clicked)
        self.help_button.clicked.connect(self.help_button_clicked)
        self.cancel_button.clicked.connect(self.cancel_button_clicked)
        self.true_fraction.setText("0.5")

    def ok_button_clicked(self):
        print("OK button clicked")
        true_fraction = float(self.true_fraction.toPlainText())
        calculate_error = self.checkError.isChecked()
        time_ = time.time()
        self.parent.pept_pipeline[f"HDBSCAN_{time_}"] = {"function": tracking.HDBSCAN, "name": "tracking.HDBSCAN", "kwargs": {"true_fraction": true_fraction, "max_tracers": self.parent.maxtracer},"update": True, "skip": False}
        self.parent.pipeline_execution_order.append(f"HDBSCAN_{time_}")
        self.parent.module_list.addItem(f"HDBSCAN_{time_}")
        self.parent.pept_pipeline[f"split_{time_}"] = {"function": lambda error: tracking.SplitLabels() + tracking.Centroids(error = error),"name": "tracking.SplitLabels() + tracking.Centroids", "kwargs": {"error": calculate_error},"update": True, "skip": False}
        self.parent.pipeline_execution_order.append(f"split_{time_}")
        self.parent.module_list.addItem(f"split_{time_}")
        self.parent.plot_item = f"split_{time_}"
        self.close()

    def cancel_button_clicked(self):
        print("Cancel button clicked")
        self.close()

    def help_button_clicked(self):
        print("Help button clicked")
        self.parent.PlotlyPlotRegion.setUrl(QUrl("https://pept.readthedocs.io/en/latest/manual/generated/pept.tracking.HDBSCAN.html?highlight=HDBscan"))
        self.close()