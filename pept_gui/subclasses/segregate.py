from PyQt5.QtWidgets import (
    QApplication, QDialog, QMainWindow, QMessageBox, QFileDialog, QLabel,QTextEdit
)
import pept
import pept.tracking as tracking
import time
from PyQt5.uic import loadUi

class Segregate(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        loadUi("ui/segregate.ui", self)
        self.ok_button.clicked.connect(self.ok_button_clicked)
        self.cancel_button.clicked.connect(self.cancel_button_clicked)
        self.window.setText("10")
        self.cut_distance.setText("5")
        self.min_traj_size.setText("10")

    def ok_button_clicked(self):
        print("OK button clicked")
        window = float(self.window.toPlainText())
        cut_distance = float(self.cut_distance.toPlainText())
        min_traj_size = int(self.min_traj_size.toPlainText())
        time_ = time.time()
        self.parent.pept_pipeline[f"Segregate_{time_}"] = {"function": tracking.Segregate,"name": "tracking.Segregate", "kwargs": {"window": window,"cut_distance": cut_distance,"min_trajectory_size": min_traj_size},"update": True, "skip": False}
        self.parent.pipeline_execution_order.append(f"Segregate_{time_}")
        self.parent.module_list.addItem(f"Segregate_{time_}")
        self.parent.plot_item = f"Segregate_{time_}"
        self.close()

    def cancel_button_clicked(self):
        print("Cancel button clicked")
        self.close()
