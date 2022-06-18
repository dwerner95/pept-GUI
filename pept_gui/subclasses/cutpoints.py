import os
import time

import pept
import pept.tracking as tracking
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QTextEdit,
)
from PyQt5.uic import loadUi


class Cutpoints(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        here = os.path.dirname(os.path.abspath(__file__))
        loadUi(os.path.join(here, "..", "ui", "cutpoints.ui"), self)
        self.ok_button.clicked.connect(self.ok_button_clicked)
        self.cancel_button.clicked.connect(self.cancel_button_clicked)
        self.max_distance.setText("0.1")

    def ok_button_clicked(self):
        print("OK button clicked")
        max_distance = float(self.max_distance.toPlainText())
        time_ = time.time()
        self.parent.pept_pipeline[f"Cutpoints_{time_}"] = {
            "function": tracking.Cutpoints,
            "name": "tracking.Cutpoints",
            "kwargs": {"max_distance": max_distance},
            "update": True,
            "skip": False,
        }
        self.parent.pipeline_execution_order.append(f"Cutpoints_{time_}")
        self.parent.module_list.addItem(f"Cutpoints_{time_}")
        self.close()

    def cancel_button_clicked(self):
        print("Cancel button clicked")
        self.close()
