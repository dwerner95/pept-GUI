from PyQt5.QtWidgets import (
    QApplication, QDialog, QMainWindow, QMessageBox, QFileDialog, QLabel,QTextEdit
)
import pept
import pept.tracking as tracking
import time
from PyQt5.uic import loadUi
import os
class Birmingham(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        here = os.path.dirname(os.path.abspath(__file__))
        loadUi(os.path.join(here,"..", "ui","birmingham.ui"), self)
        self.ok_button.clicked.connect(self.ok_button_clicked)
        self.cancel_button.clicked.connect(self.cancel_button_clicked)
        self.fopt.setText("0.2")

    def ok_button_clicked(self):
        print("OK button clicked")
        fopt = float(self.fopt.toPlainText())
        time_ = time.time()
        self.parent.pept_pipeline[f"Birmingham_{time_}"] = {"function": tracking.BirminghamMethod, "name": "tracking.BirminghamMethod", "kwargs": {"fopt": fopt,},"update": True, "skip": False}
        self.parent.pipeline_execution_order.append(f"Birmingham_{time_}")
        self.parent.module_list.addItem(f"Birmingham_{time_}")
        self.parent.plot_item = f"Birmingham_{time_}"
        self.close()

    def cancel_button_clicked(self):
        print("Cancel button clicked")
        self.close()
