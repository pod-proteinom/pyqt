import os
import re
import sys

from PyQt5.QtWidgets import QAction, qApp
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget


class Scene(QWidget):
    def __init__(self):
        super().__init__()
        self.mainEditor = QTextEdit(self)
        self.leftEditor = QTextEdit(self)
        self.rightEditor = QTextEdit(self)
        self.about = QMessageBox(self)
        self.initUI()

    def initUI(self):
        verLayout = QVBoxLayout()
        horLayout = QHBoxLayout()
        horLayout.addWidget(self.leftEditor)
        horLayout.addWidget(self.rightEditor)

        verLayout.addWidget(self.mainEditor)
        verLayout.addLayout(horLayout)
        self.setLayout(verLayout)

        self.about.setWindowTitle("About")
        self.about.setIcon(QMessageBox.Information)
        self.about.setText("Written by Alexandr Tatarchuk")

    def initEditors(self, fileText):
        self.mainEditor.setText(self.getMainEditorText(fileText))
        self.leftEditor.setText(self.getLeftEditorText(fileText))
        self.rightEditor.setText(self.getRightEditorText(fileText))

    def getMainEditorText(self, text):
        result = []
        for line in text:
            if re.match(r"^\*.*", line) is None:
                result.append(line)
                result.append("\n")
        return "".join(result)

    def getRightEditorText(self, text):
        result = []
        for line in text:
            subcktSearch = re.search(r"^\.subckt ([\w]+) ([\w]+\s+){2,}\w+", line, re.I)
            if subcktSearch:
                result.append(subcktSearch.group(1))
                result.append("\n")
        return "".join(result)

    def getLeftEditorText(self, text):
        result = []
        netlist = "\n".join(text)
        allSubckts = re.findall(r"^\.subckt.*?\.ends", netlist, re.I | re.DOTALL | re.M)
        for subckt in allSubckts:
            subcktSearch = re.search(r"^\.subckt ([\w]+)(.*?)\.ends", subckt, re.I | re.DOTALL)
            if subcktSearch:
                hierarchySubckt = re.search(r"^x.+", subcktSearch.group(2), re.I | re.M)
                if hierarchySubckt is None:
                    result.append(subcktSearch.group(1))
                    result.append("\n")
        return "".join(result)

    def showAbout(self):
        self.about.show()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.scene = Scene()
        self.setCentralWidget(self.scene)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("PyQt App")
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu("&File")
        openAction = QAction("&Open", self)
        quitAction = QAction("&Exit", self)
        fileMenu.addAction(openAction)
        fileMenu.addAction(quitAction)
        fileMenu.triggered.connect(self.fileMenuTrigger)

        helpMenu = menuBar.addMenu("&Help")
        aboutAction = QAction("&About", self)
        helpMenu.addAction(aboutAction)
        helpMenu.triggered.connect(self.openAbout)
        self.show()

    def fileMenuTrigger(self, s):
        signal = s.text()
        if signal == "&Open":
            self.openFile()
        elif signal == "&Exit":
            qApp.quit()

    def openFile(self):
        filename = QFileDialog.getOpenFileName(self, "Open spice file", os.getenv("HOME"))
        if filename[0] != "":
            with open(filename[0], "r") as f:
                self.scene.initEditors(f.read().splitlines())

    def openAbout(self):
        self.scene.showAbout()

# Back up the reference to the exceptionhook
sys._excepthook = sys.excepthook

def my_exception_hook(exctype, value, traceback):
    # Print the error and traceback
    print(exctype, value, traceback)
    # Call the normal Exception hook after
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)

# Set the exception hook to our wrapping function
sys.excepthook = my_exception_hook

app = QApplication(sys.argv)
mainWindow = MainWindow()
try:
    sys.exit(app.exec_())
except:
    print("Exiting")