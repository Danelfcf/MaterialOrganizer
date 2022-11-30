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
        self.scrollFilters.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        #ExcersicesTab
        self.ButtonClearAll.clicked.connect(self.clearAllSelected)
        self.ButtonApply.clicked.connect(self.applyFilters)

        #Selectedtab
        self.ButtonPrint.clicked.connect(self.Print)

        # trying to enable drag and drop
        self.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.tableWidget.setDragEnabled(True)
        self.tableWidget.viewport().setAcceptDrops(True)
        self.tableWidget.setDropIndicatorShown(True)
        self.tableWidget.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.InternalMove)

        self.db = False
        self.baseCol = ['Option_1', 'ID']
        self.columns = False
        self.loadedData = False
        self.DataDepth = 10

        self.update()

    def dbLink(self, x):
        self.db = x
        self.columns = self.db.columnNames()
        self.tableWidget.setColumnCount(len(self.columns + self.baseCol))
        self.tableWidget.setHorizontalHeaderLabels(self.baseCol + self.columns)
        self.loadData()

    def loadTags(self):
        for i in self.columns:
            self.TagsH.insertWidget(self.TagsH.count() - 1, ColList(f"{i}", parent=self))
            self.TagsH.itemAt(self.TagsH.count() - 2).widget().loadlist(self.db.columnsDistinct(i))

    def applyFilters(self):
        for widget in self.scrollFilters.findChildren(ColList):
            widget.SelectedItems()

    def loadData(self):
        self.loadedData = []
        a = self.db.readAll()
        for i in a:
            self.loadedData.append(Row(self.baseCol + self.columns, i).row)
        for i in range(len(self.loadedData)):
            self.tableWidget.insertRow(i)
            for j in range(len(self.loadedData[i])):
                self.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem(str(self.loadedData[i][j])))
        # self.tableWidget.setModal(Table)

    def clearAllSelected(self):
        for widget in self.scrollFilters.findChildren(ColList):
            widget.clearSel()
    def Print(self):
        printer = QtPrintSupport.QPrinter()
        printDialog = QtPrintSupport.QPrintDialog()
        if printDialog.exec() == QtPrintSupport.QPrintDialog.accepted:
            self.handle_paint_request(printer)


class DatabaseSQLite:

    def __init__(self):
        self.dbPath = False
        self.Create()

    def Create(self, path='', name="database.db"):
        """
        Connects to a database in path, default is active file, named database.db. If
        Database does not exist it will be created
        :param path: (str) database folder's path, must be set according to OS
        :param name: (str) database name
        :return: True if database connection is valid
                 str if database connection Failed
        """
        try:
            db = sqlite3.connect(path+name)
            print(sqlite3.version)
        except Error as e:
            return e
        finally:
            if db:
                db.close()
                self.dbPath= path + name
                return True

    def RunCommand(self, c, inputString):
        try:
            print(inputString)
            return c.execute(inputString)
        except Error as e:
            return e
    def Connect(self, command, *args, **kwargs):
        """
        Input function, args and kwargs.
        print(db.Connect(db.RunCommand, sql_create_tasks_table))
        :param command: function
        :param args: passed function's arguments
        :param kwargs: passed function's keyword arguments
        :return: passed functions return or Error String
        """
        db = sqlite3.connect(self.dbPath)
        curser = db.cursor()
        rt=True
        try:
            rt = command(curser, *args, **kwargs).fetchall()
        except Error as e:
            return e
        finally:
            if db:
                db.close()
                return rt

    def CreateTable(self, c, table, Cols=[], types=[], adds=[]):
        """

        :param table:
        :param Cols:
        :param types:
        :param adds:
        """
        if(isinstance(table, str)) & \
          (isinstance(Cols, list)) & \
          (isinstance(types, list)) & \
          (isinstance(adds, list)):
            cmdstr=f'CREATE TABLE IF NOT EXISTS {table}(\n'
            for name, typ, add in list(itertools.zip_longest(Cols, types, adds, fillvalue="")):
                cmdstr += f'{name} {typ} {add},\n'
            cmdstr = cmdstr[:-2]+");"

            return self.RunCommand(c, cmdstr)

        else:
            return False

    def add(self, table, data={}):
        part1= f"INSERT INTO {table}("
        part2= f"VALUES("
        for col, val in zip(data.keys(), data.values()):
            part1 += f"'{col}', "
            part2 += f"'{val}', "

        cmdstr = part1[:-2]+") " + part2[:-2]+");"
        return self.Connect(self.RunCommand, cmdstr)

    def columnNames(self, table="Material"):
        a = db.Connect(self.RunCommand, f"select name from pragma_table_info('{table}')")
        return list(map(lambda x: x[0], a))




class DatabaseTinyDB:

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

    def find(self, field, x):
        '''
        Example usage: print(db.find(['type'], ['apple']))
        :param field: (str) database 'column' to be searched for
        :param x: (str) value looked for
        :return: list[dic{}]
        '''
        #return self.db.search(self.q[tuple(field)].one_of(x))
        print(self.db.search(self.q[tuple(field)].one_of(field)))
        return []#self.db.search(self.db.table('_default').all())

    def columnsDistinct(self, x):
        '''
        Must be changed, as db gets bigger this will slow down like hell. does not take nested lists into account!!
        Used to get all valid items within a datacolumn
        Example usage: columnsDistinct('type')
        :param x: (str) 'column' to search for distinct items
        :return: list[]
        '''
        values = []
        for i in self.db.search(self.q[x].exists()):
            if i.get(x) not in values:
                values.append(i.get(x))
        return values

    def columnNames(self):
        values = []
        for i in self.db.table('_default').all()[0]:
            if i not in values:
                values.append(i)
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
