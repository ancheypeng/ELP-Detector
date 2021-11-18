import sys
import ctypes
import subprocess
import images_qr  # necessary to load icons properly
import sys

# Import QApplication and the required widgets from PyQt5.QtWidgets
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, \
    QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QFileDialog, \
    QPlainTextEdit


__version__ = '0.1'
__author__ = 'Anchey Peng'


class DetectorUi(QMainWindow):
    """ELP Detector View (GUI)."""

    def __init__(self):
        """View initializer."""
        super().__init__()
        # Set some main window's properties
        self.setWindowTitle('ELP Detector')
        self.setWindowIcon(QtGui.QIcon(':/elp-logo.png'))
        # self.setFixedSize(1000, 350)
        # Set the central widget and the general layout
        self.generalLayout = QVBoxLayout()
        self.generalLayout.setContentsMargins(20, 20, 20, 20)
        self._centralWidget = QWidget(self)
        self.setCentralWidget(self._centralWidget)
        self._centralWidget.setLayout(self.generalLayout)

        # Create the display and the buttons
        self._createFolderSelect()
        self._createOutputView()
        self._createButtons()

    def _createFolderSelect(self):
        """Create the folder selectors"""

        folderSelectLayout = QGridLayout()

        # Create the detector script folder widget
        scriptFolderLabel = QLabel("Script Folder: ")
        self.scriptFolderEdit = QLineEdit()
        self.scriptFolderEdit.setMinimumWidth(600)
        self.scriptFolderButton = QPushButton('Browse')

        folderSelectLayout.addWidget(scriptFolderLabel, 0, 0)
        folderSelectLayout.addWidget(self.scriptFolderEdit, 0, 1)
        folderSelectLayout.addWidget(self.scriptFolderButton, 0, 2)

        # Create the sound folder widget
        soundFolderLabel = QLabel("Sound File Folder: ")
        self.soundFolderEdit = QLineEdit()
        self.soundFolderEdit.setMinimumWidth(600)
        self.soundFolderButton = QPushButton('Browse')

        folderSelectLayout.addWidget(soundFolderLabel, 1, 0)
        folderSelectLayout.addWidget(self.soundFolderEdit, 1, 1)
        folderSelectLayout.addWidget(self.soundFolderButton, 1, 2)

        # Create the output folder widget
        outputFolderLabel = QLabel("Output Folder: ")
        self.outputFolderEdit = QLineEdit()
        self.outputFolderEdit.setMinimumWidth(600)
        self.outputFolderButton = QPushButton('Browse')

        folderSelectLayout.addWidget(outputFolderLabel, 2, 0)
        folderSelectLayout.addWidget(self.outputFolderEdit, 2, 1)
        folderSelectLayout.addWidget(self.outputFolderButton, 2, 2)

        # Add the display to the general layout
        self.generalLayout.addLayout(folderSelectLayout)

    def _createButtons(self):
        """Create run and cancel buttons"""
        btnLayout = QHBoxLayout()

        self.runBtn = QPushButton('Run')
        self.runBtn.setFixedWidth(200)

        self.cancelBtn = QPushButton('Cancel')
        self.cancelBtn.setFixedWidth(200)

        btnLayout.addWidget(self.runBtn, 1, alignment=Qt.AlignRight)
        btnLayout.addWidget(self.cancelBtn, 0, alignment=Qt.AlignRight)

        self.generalLayout.addLayout(btnLayout)

    def _createOutputView(self):
        """Create display to view script output"""
        self.outputView = QPlainTextEdit()
        self.outputView.setFont(QtGui.QFont('Courier New'))
        self.outputView.setMinimumHeight(500)
        # self.outputView.setReadOnly(True)
        self.outputView.setStyleSheet("margin: 20px")
        self.generalLayout.addWidget(self.outputView)

    def appendDisplayText(self, text):
        """Set outputView's text."""
        # self.outputView.appendPlainText(text)
        self.outputView.moveCursor(QtGui.QTextCursor.End)
        self.outputView.insertPlainText(text)
        self.outputView.repaint()

    def setDisplayText(self, text):
        """Set outputView's text."""
        self.outputView.setPlainText(text)

    def displayText(self):
        """Get outputView's text."""
        return self.outputView.toPlainText()

    def clearDisplay(self):
        """Clear the outputView."""
        self.outputView.setPlainText("")
        self.outputView.setFocus()


class SubprocessWorker(QObject):
    writeOutput = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, scriptDir, dataDir, spectDir):
        super().__init__()
        self.scriptDir = scriptDir
        self.inferencePipeline = ["python", "-u", "Inference_pipeline.py",
                                  "--process_data", "--make_predictions", "--model_0",
                                  "2_Stage_Model/first_stage.pt",
                                  "--model_1", "2_Stage_Model/second_stage.pt",
                                  "--data_dir", dataDir, "--spect_out", spectDir]

        self.dataGeneration = ["python", "-u", "Inference_pipeline.py",
                               "--process_data", "--data_dir", dataDir, "--spect_out", spectDir]

        # uses dataDir for the spect directory bc spect output does not work properly
        self.modelPredictions = ["python", "-u", "Inference_pipeline.py",
                                 "--make_predictions",
                                 "--model_0", "2_Stage_Model/first_stage.pt",
                                 "--model_1", "2_Stage_Model/second_stage.pt",
                                 "--spect_path", dataDir]

    def run(self):

        steps = [self.inferencePipeline,
                 self.dataGeneration, self.modelPredictions]

        for step in steps:
            process = subprocess.Popen(
                step, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=self.scriptDir)
            for line in iter(process.stdout.readline, b''):
                strLine = line.decode(sys.stdout.encoding)

                # comment this line out before bundling to exe
                # sys.stdout.write(strLine)
                self.writeOutput.emit(strLine)

        print("Detector run has completed. ")

        self.finished.emit()


class GuiController:
    """Gui Controller Class"""

    def __init__(self, view):
        """Controller Initializer"""
        self._view = view
        # Connect signals and slots
        self._connectSignals()

    def _runDetector(self):

        scriptDir = self._view.scriptFolderEdit.text()
        dataDir = self._view.soundFolderEdit.text()
        spectDir = self._view.outputFolderEdit.text()

        # Create QThread object
        self.thread = QThread()
        # Create a worker object
        self.worker = SubprocessWorker(scriptDir, dataDir, spectDir)

        # Move worker to the thread
        self.worker.moveToThread(self.thread)
        # Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.writeOutput.connect(self._view.appendDisplayText)
        # Start the thread
        self.thread.start()

    def _openFolderSelect(self, lineEdit):
        """Opens folder select dialog and sets the text of lineEdit to the folder path"""
        folder = str(QFileDialog.getExistingDirectory(
            None, "Select Directory"))
        lineEdit.setText(folder)

    def _connectSignals(self):
        """Connects signals and slots"""
        # Connect cancel button to close window
        self._view.cancelBtn.clicked.connect(QApplication.quit)
        # Connect run button to run the detector
        self._view.runBtn.clicked.connect(self._runDetector)

        # Connect folder browse buttons to open folder select dialog
        self._view.scriptFolderButton.clicked.connect(
            lambda: self._openFolderSelect(self._view.scriptFolderEdit))
        self._view.soundFolderButton.clicked.connect(
            lambda: self._openFolderSelect(self._view.soundFolderEdit))
        self._view.outputFolderButton.clicked.connect(
            lambda: self._openFolderSelect(self._view.outputFolderEdit))


'''
Traceback (most recent call last):
  File "gui.py", line 171, in _runDetector
  File "subprocess.py", line 800, in __init__
  File "subprocess.py", line 1207, in _execute_child
OSError: [WinError 123] The filename, directory name, or volume label syntax is incorrect

'''


def main():
    """Main function."""

    # Set AppUserModelID
    # Necessary to load windows taskbar icon
    myappid = u'ElephantListeningProject.Detector.GUI.0.1'  # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    # Create an instance of QApplication
    detectorUi = QApplication(sys.argv)
    # Show the calculator's GUI
    view = DetectorUi()
    view.show()
    # Create instances of controller
    GuiController(view=view)
    # Execute the calculator's main loop
    sys.exit(detectorUi.exec_())


if __name__ == '__main__':
    main()
