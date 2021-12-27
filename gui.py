import sys
import ctypes
import subprocess
import images_qr  # necessary to load icons properly
import sys

# Import QApplication and the required widgets from PyQt5.QtWidgets
from PyQt5.QtCore import Qt, QObject, QThread, QTimer, QTime, pyqtSignal
from PyQt5.QtGui import QIcon, QFont, QTextCursor
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, \
    QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QFileDialog, \
    QPlainTextEdit, QDialog

from help_dialog import HelpDialog


__version__ = '0.1'
__author__ = 'Anchey Peng'


class DetectorUi(QMainWindow):
    """ELP Detector View (GUI)."""

    def __init__(self):
        """View initializer."""
        super().__init__()
        # Set some main window's properties
        self.setWindowTitle('ELP Detector')
        self.setWindowIcon(QIcon(':/elp-logo.png'))

        # Set the central widget and the general layout
        self.generalLayout = QVBoxLayout()
        self.generalLayout.setContentsMargins(10, 10, 10, 10)
        self._centralWidget = QWidget(self)
        self.setCentralWidget(self._centralWidget)
        self._centralWidget.setLayout(self.generalLayout)

        # Create the display and the buttons
        self._createFolderSelect()
        self._createOutputView()
        self._createProgressIndicator()
        self._createButtons()

    def _createFolderSelect(self):
        """Create the folder selectors"""

        folderSelectLayout = QGridLayout()

        # Create the detector script folder widget
        scriptFolderLabel = QLabel("Script Folder: ")
        self.scriptFolderEdit = QLineEdit()
        self.scriptFolderEdit.setMinimumWidth(300)
        self.scriptFolderButton = QPushButton('Browse')

        folderSelectLayout.addWidget(scriptFolderLabel, 0, 0)
        folderSelectLayout.addWidget(self.scriptFolderEdit, 0, 1)
        folderSelectLayout.addWidget(self.scriptFolderButton, 0, 2)

        # Create the sound folder widget
        soundFolderLabel = QLabel("Sound File Folder: ")
        self.soundFolderEdit = QLineEdit()
        self.soundFolderEdit.setMinimumWidth(300)
        self.soundFolderButton = QPushButton('Browse')

        folderSelectLayout.addWidget(soundFolderLabel, 1, 0)
        folderSelectLayout.addWidget(self.soundFolderEdit, 1, 1)
        folderSelectLayout.addWidget(self.soundFolderButton, 1, 2)

        # Create the output folder widget
        outputFolderLabel = QLabel("Output Folder: ")
        self.outputFolderEdit = QLineEdit()
        self.outputFolderEdit.setMinimumWidth(300)
        self.outputFolderButton = QPushButton('Browse')

        folderSelectLayout.addWidget(outputFolderLabel, 2, 0)
        folderSelectLayout.addWidget(self.outputFolderEdit, 2, 1)
        folderSelectLayout.addWidget(self.outputFolderButton, 2, 2)

        # Add the display to the general layout
        self.generalLayout.addLayout(folderSelectLayout)

    def _createButtons(self):
        """Create run and cancel buttons"""
        btnLayout = QHBoxLayout()

        self.helpBtn = QPushButton('Help')
        # self.helpBtn.setFixedWidth(200)

        self.runBtn = QPushButton('Run')
        # self.runBtn.setFixedWidth(200)

        self.cancelBtn = QPushButton('Cancel')
        # self.cancelBtn.setFixedWidth(200)

        btnLayout.addWidget(self.helpBtn, 1, alignment=Qt.AlignRight)
        btnLayout.addWidget(self.runBtn, 0, alignment=Qt.AlignRight)
        btnLayout.addWidget(self.cancelBtn, 0, alignment=Qt.AlignRight)

        self.generalLayout.addLayout(btnLayout)

    def _createOutputView(self):
        """Create display to view script output"""
        self.outputView = QPlainTextEdit()
        self.outputView.setFont(QFont('Courier New'))
        self.outputView.setMinimumHeight(250)
        # self.outputView.setReadOnly(True)
        self.outputView.setStyleSheet("margin: 10px")
        self.generalLayout.addWidget(self.outputView)

    def _createProgressIndicator(self):
        # creating a label object
        self._timeLabel = QLabel()

        # adding label to the layout
        self.generalLayout.addWidget(self._timeLabel)

        self._t = QTime()
        self._timer = QTimer(self, interval=100, timeout=self._updateTime)

        self._timeStr = "00:00"

        self._timeLabel.hide()

    def startTimer(self):
        self._timer.start()
        self._t.start()
        self._timeLabel.show()

    def stopTimer(self):
        self._timer.stop()

        self._timeLabel.setText(
            "Run complete. Total Time: " + self._timeStr)

    def _updateTime(self):

        def formatTime(h, m, s):
            h = str(h)
            m = str(m)
            s = str(s)
            if (len(h) < 2):
                h = "0" + h
            if (len(m) < 2):
                m = "0" + m
            if (len(s) < 2):
                s = "0" + s

            if (h == "00"):
                return m + ":" + s
            else:
                return h + ":" + m + ":" + s

        secs = QTime.elapsed(self._t) // 1000
        hours = secs // 3600
        secs %= 3600
        minutes = secs // 60
        secs %= 60

        self._timeStr = formatTime(hours, minutes, secs)

        self._timeLabel.setText(
            "Time Elapsed: " + self._timeStr)

    def showHelpDialog(self):
        self.helpDialog = HelpDialog()
        self.helpDialog.exec()


    def appendDisplayText(self, text):
        """Set outputView's text."""
        # self.outputView.appendPlainText(text)
        self.outputView.moveCursor(QTextCursor.End)
        if(text != ""):
            self.outputView.insertPlainText(text)
            self.outputView.update()

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
    runStarted = pyqtSignal()
    writeOutput = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, scriptDir, dataDir, spectDir):
        super().__init__()
        self.scriptDir = scriptDir
        self.dataDir = dataDir
        self.spectDir = spectDir

        self.inferencePipeline = ["python", "-u", "Inference_pipeline.py",
                                  "--process_data", "--make_predictions",
                                  "--model_0", "2_Stage_Model/first_stage.pt",
                                  "--model_1", "2_Stage_Model/second_stage.pt",
                                  "--data_dir", self.dataDir, "--spect_out", self.spectDir]

        # self.dataGeneration = ["python", "-u", "Inference_pipeline.py",
        #                        "--process_data", "--data_dir", dataDir, "--spect_out", spectDir]

        # # uses dataDir for the spect directory bc spect output does not work properly
        # self.modelPredictions = ["python", "-u", "Inference_pipeline.py",
        #                          "--make_predictions",
        #                          "--model_0", "2_Stage_Model/first_stage.pt",
        #                          "--model_1", "2_Stage_Model/second_stage.pt",
        #                          "--spect_path", dataDir]

    def run(self):

        # steps = [self.inferencePipeline,
        #          self.dataGeneration, self.modelPredictions]
        if (not self.scriptDir or not self.dataDir or not self.spectDir):
            if (not self.scriptDir):
                print("Please select a script directory before running.")
            if (not self.dataDir):
                print("Please select a data file directory before running.")
            if (not self.spectDir):
                print("Please select a spectrogram file directory before running.")

            self.finished.emit()
            return

        self.runStarted.emit()

        steps = [self.inferencePipeline]

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
        self.worker.finished.connect(self._view.stopTimer)

        self.thread.finished.connect(self.thread.deleteLater)

        self.worker.runStarted.connect(self._view.startTimer)
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

        # Connect help button to show help dialog
        self._view.helpBtn.clicked.connect(self._view.showHelpDialog)

        # Connect run button to run the detector
        self._view.runBtn.clicked.connect(self._runDetector)

        # Connect cancel button to close window
        self._view.cancelBtn.clicked.connect(QApplication.quit)
        

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
    # Show the GUI
    view = DetectorUi()
    view.show()
    # Create instances of controller
    GuiController(view=view)
    # Execute the main loop
    sys.exit(detectorUi.exec_())


if __name__ == '__main__':
    main()
