import sys
from PySide import QtGui
import piano_control
#from piano_control import run as run_piano_control

class PianoControl(QtGui.QWidget):
    
    def __init__(self):
        super(PianoControl, self).__init__()
        self.initUI()
        
    def initUI(self):
        openButton = QtGui.QPushButton("Open")
        openButton.clicked.connect(self.showDialog)
        self.fileNameBox = QtGui.QLineEdit()
        self.fileNameBox.setReadOnly(True)
        runButton  = QtGui.QPushButton("Run")
        runButton.clicked.connect(self.run)
        
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(openButton)
        hbox.addWidget(self.fileNameBox)
        hbox.addWidget(runButton)
        
        self.setLayout(hbox)
        self.setGeometry(150, 150, 500, 100)
        self.setWindowTitle('Piano control')
        self.show()
        
    def showDialog(self):
        fname, _ = QtGui.QFileDialog.getOpenFileName(self, 'Open file',
            'C:/Users/amcm023/Dropbox/ses/Gregs_Piano/')
        self.fileNameBox.setText(fname)
        
    def run(self):
        fname = self.fileNameBox.text()
        piano_control.run(fname)

def main():
    app = QtGui.QApplication(sys.argv)
    prog = PianoControl()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
