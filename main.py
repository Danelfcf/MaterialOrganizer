from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPalette, QColor
from PyQt6 import uic
# Only needed for access to command line arguments
import sys
# Only to access database
from tinydb import TinyDB, Query

class list(QWidget):

    def __init__(self, color):
        super().__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(color))
        self.setPalette(palette)
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi("MainWindow.ui", self)

        self.TagsH.addWidget(list('red'))
        self.TagsH.addWidget(list('red'))
        self.TagsH.addWidget(list('red'))
        self.TagsH.addWidget(list('red'))
        self.TagsH.addWidget(list('red'))
        self.TagsH.addWidget(list('red'))

class Database():
    def __init__(self):
        self.db = TinyDB('testdb.json')
        self.q = Query()
    def add(self, x):
        '''

        :param x:
        :return:
        '''
        self.db.insert(x)

    def readAll(self):
        '''

        :return:
        '''
        return self.db.all()

    def find(self, x):
        '''

        :param x:
        :return:
        '''
        return self.db.search(x)

    def columnsDistinct(self, x, col):
        '''

        :param x:
        :param col:
        :return:
        '''
        values=[]
        for i in self.db.search(x.exists()):
            if i.get(col) not in values:
                values.append(i.get(col))
        return values


if __name__ == '__main__':
    db = Database()
    q = db.q
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()


    #print(db.find(q.type == 'apple'))
    #db.add({'type': 'apple', 'count': 7})

    #db.columnsDistinct(q.type, 'type')
