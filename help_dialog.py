import os
import sys
import subprocess

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, \
    QPlainTextEdit, QDialog

class HelpDialog(QDialog):
  def __init__(self):
    super().__init__()

    self.bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))

    self.setWindowTitle("ELP Detector Help")
    self.setWindowIcon(QIcon(':/elp-logo.png'))
    self.setMinimumWidth(400)
    self.setMinimumHeight(300)

    # Hides "?" button next to close button on the dialog menu bar
    self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

    self.helpLayout = QVBoxLayout()
    self.helpLayout.setContentsMargins(10, 10, 10, 10)
    self.setLayout(self.helpLayout)

    self._createInstructions()
    self._createButtons()

    self._connectSignals()
    
  def _createInstructions(self):

    # Use this for one file bundling
    helpFilePath = os.path.abspath(os.path.join(self.bundle_dir, "help.txt"))
    
    # Use this for one directory bundling
    #helpFilePath = "help.txt"
    
    
    helpFile = open(helpFilePath)

    

    helpText = helpFile.read()
    helpFile.close()

    instructions = QPlainTextEdit()
    instructions.setReadOnly(True)
    instructions.setPlainText(helpText)
    self.helpLayout.addWidget(instructions)

  def _createButtons(self):
    btnLayout = QHBoxLayout()

    self.okBtn = QPushButton('Ok')

    self.installBtn = QPushButton('Install Dependencies')
    self.installBtn.setMinimumWidth(125)

    btnLayout.addWidget(self.installBtn, 1, alignment=Qt.AlignRight)
    btnLayout.addWidget(self.okBtn, 0, alignment=Qt.AlignRight)

    self.helpLayout.addLayout(btnLayout)

  def _installDependencies(self):

    # Use this for one file bundling
    requirementsPath = os.path.abspath(os.path.join(self.bundle_dir, "detector_requirements.txt"))

    # Use this for one directory bundling
    #requirementsPath = "detector_requirements.txt"

    subprocess.check_call(["python", "-m", "pip", "install", "-r", requirementsPath])

    print("\nDependencies Installed")


  def _connectSignals(self):
    self.okBtn.clicked.connect(self.close)
    self.installBtn.clicked.connect(self._installDependencies)
        