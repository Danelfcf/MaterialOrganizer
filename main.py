import itertools

from PyQt6 import QtCore, QtGui, QtWidgets, QtPrintSupport
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPalette, QColor
from PyQt6 import uic
# Only needed for access to command line arguments
import sys
# Only to access database
from tinydb import TinyDB, Query, where
import sqlite3
from sqlite3 import Error
from itertools import zip_longest

class Row:
    def __init__(self, cols, data):
        self.row = []
        for i in cols:
            try:
                self.row.append(data[i])
            except KeyError:
                self.row.append("-")
                # self.row.append(QtWidgets.QCheckBox())

class ColList(QWidget):
    """lmlml"""
    def __init__(self, col, parent=None):
        super().__init__(parent)
        # Load the GUI
        uic.loadUi("Listwidget.ui", self)
        self.title = col
        self.groupBox.setTitle(col)
        self.listWidget.setSortingEnabled(True)
        self.listWidget.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.ButtonClear.clicked.connect(self.clearSel)

    def loadlist(self, x):
        self.listWidget.addItems([str(i) for i in x])
        # self.listWidget.setMinimumWidth(self.listWidget.sizeHintForColumn(0))

    def clearSel(self):
        self.listWidget.clearSelection()
    def SelectedItems(self):
        return ([item.text() for item in self.listWidget.selectedItems()])
    def SC(self):
        print("hi")

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
