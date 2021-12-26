from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, \
    QPlainTextEdit, QDialog

class HelpDialog(QDialog):
  def __init__(self):
    super().__init__()

    self.setWindowTitle("ELP Detector Help")
    self.setWindowIcon(QIcon(':/elp-logo.png'))
    self.setMinimumWidth(800)
    self.setMinimumHeight(500)

    # Hides "?" button next to close button on the dialog menu bar
    self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

    self.helpLayout = QVBoxLayout()
    self.helpLayout.setContentsMargins(20, 20, 20, 20)
    self.setLayout(self.helpLayout)

    helpFile = open("help.txt")
    helpText = helpFile.read()
    helpFile.close()

    instructions = QPlainTextEdit()
    instructions.setReadOnly(True)
    instructions.setPlainText(helpText)
    self.helpLayout.addWidget(instructions)

    btnLayout = QHBoxLayout()

    self.okBtn = QPushButton('Ok')
    self.okBtn.setFixedWidth(200)

    
    btnLayout.addWidget(self.okBtn, 0, alignment=Qt.AlignRight)

    self.helpLayout.addLayout(btnLayout)



    # self.helpDialog.exec()

  # def showHelpDialog(self):
  #       self.helpDialog = QDialog()
        