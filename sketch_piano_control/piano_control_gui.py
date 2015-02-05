import sys
from PySide import QtGui
from PySide.QtCore import QCoreApplication
import piano_control as pc
import time
#from piano_control import run as run_piano_control

'''
TO DO
-----
doesn't regain focus after another window has been moved to the front
'''

def get_last_trial_num(entries):
    return entries[-1][0]

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
        
        self.progressBar = QtGui.QProgressBar()
        self.progressBar.setRange(0, 100)
        self.progressBar.setFormat('%v / %m')
        self.progressBar.setValue(0)
        
        stopButton = QtGui.QPushButton("Stop")
        self.do_stop = False
        stopButton.clicked.connect(self.stop)
        
        hbox0 = QtGui.QHBoxLayout()
        hbox0.addWidget(openButton)
        hbox0.addWidget(self.fileNameBox)
        hbox0.addWidget(runButton)
        
        hbox1 = QtGui.QHBoxLayout()
        hbox1.addWidget(self.progressBar)
        hbox1.addWidget(stopButton)
        
        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(hbox0)
        vbox.addLayout(hbox1)
        
        self.setLayout(vbox)
        self.setGeometry(150, 150, 500, 100)
        self.setWindowTitle('Piano Control')
        self.show()
        
    def showDialog(self):
        fname, _ = QtGui.QFileDialog.getOpenFileName(self, 'Open file',
            'C:/Users/Matthew/Desktop/Python files/')
        self.fileNameBox.setText(fname)
        self.get_entries(fname)
        self.progressBar.setMaximum(get_last_trial_num(self.entries))
        
    def get_entries(self, file_name):
        #file_name = self.fileNameBox.text()
        self.entries = pc.read_file(file_name)
        
    def run(self):
        ser = pc.start_serial()

        # wait for reply
        for trial, bitpat, target_time in self.entries:
            if self.do_stop:
                self.do_stop = False
                break
            sys.stdout.write(bin(bitpat) + ' ')
            bitpat = pc.fix_bitpat(bitpat)
            sys.stdout.write("|")
            sys.stdout.write(' ' + bin(bitpat) + '\n')
            pc.send_command(bitpat, target_time, ser)
            sys.stdout.flush()
            while ser.inWaiting() == 0:
                QCoreApplication.processEvents()
                time.sleep(0.01) # pause for 10 ms
            rcvd = ser.read(2)
            if rcvd == 's5':
                sys.stdout.write("*")
                sys.stdout.flush()
            self.progressBar.setValue(trial)

        time.sleep(0.02)
        # clear the last timeout warning
        # this should leave an 's0' waiting for next time
        ser.read(2)
        ser.close()

    def stop(self):
        self.do_stop = True

def main():
    app = QtGui.QApplication(sys.argv)
    prog = PianoControl()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
