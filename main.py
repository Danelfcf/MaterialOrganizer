"""
main for GUI project
"""

import itertools
# Only to access database
import sqlite3
# Only needed for access to command line arguments
import sys
from sqlite3 import Error

from PyQt6 import QtCore, QtWidgets, QtPrintSupport
from PyQt6 import uic
from PyQt6.QtWidgets import QWidget

import pickle


class Row:
    """
    Build list of items to be placed in table.

    This will be changed into a pyqt widget
    """

    def __init__(self, cols, data):
        self.row = []
        for d, c in zip(data, cols):
            try:
                if d == "hyperlink":
                    self.row.append(d)
                else:
                    self.row.append(d)
            except KeyError:
                self.row.append("-")
                # self.row.append(QtWidgets.QCheckBox())


class ColList(QWidget):
    """
    Pyqt widget for listing selectable strings within a list
    """
    selection_change = QtCore.pyqtSignal()

    def __init__(self, col, parent=None):
        super().__init__(parent)
        # Load the GUI
        uic.loadUi("Listwidget.ui", self)
        self.title = col
        self.groupBox.setTitle(col)
        self.listWidget.setSortingEnabled(True)
        self.listWidget.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.listWidget.itemSelectionChanged.connect(self.selection_change)
        self.ButtonClear.clicked.connect(self.clearSel)

    def loadList(self, x):
        """
        Gets all the items to be added to the list and places them in listWidget
        :param x:
        """
        self.listWidget.addItems([str(i) for i in x])
        # self.listWidget.setMinimumWidth(self.listWidget.sizeHintForColumn(0))

    def clearSel(self):
        """
        Clears selected items in listWidget
        """
        self.listWidget.clearSelection()

    def SelectedItems(self):
        """

        :return:
        """
        return [item.text() for item in self.listWidget.selectedItems()]

    def UserSelectionChange(self):
        """
        custom signal
        """
        selection_change.emit()

    @staticmethod
    def SC():
        """
        Sanity check
        """
        print("hi")


class SQLViewer(QWidget):
    """
    Sql viewer
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        # Load the GUI
        uic.loadUi("SQLViewer.ui", self)
        self.scrollFilters.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Exercises_Tab
        self.ButtonClearAll.clicked.connect(self.clearAllSelected)
        self.ButtonApply.clicked.connect(self.applyFilters)

        # trying to enable drag and drop
        self.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.tableWidget.setDragEnabled(True)
        self.tableWidget.viewport().setAcceptDrops(True)
        self.tableWidget.setDropIndicatorShown(True)
        self.tableWidget.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.InternalMove)

        self.db = False
        self.columns = None
        self.loadedData = False
        self.DataDepth = 10

        self.update()

    def dbLink(self, x):
        """
        Receives a Database class for program to access and control
        :param x: Database class
        """
        self.db = x
        self.columns = self.db.columnNames()
        self.tableWidget.setColumnCount(len(self.columns))
        self.tableWidget.setHorizontalHeaderLabels(self.columns)
        self.loadData()

    def loadTags(self):
        """
        Creates a ColList widget for every column within the database and places
        every distinct value from each column to its corresponding widget. ie:

        id | name | date
        1  |  bob | 1990

        creates 3 widgets,
            one for id containing 1,
            one for name containing 'bob' and
            the third for date containing 1990
        """
        if self.columns:
            for i in self.columns:
                column_list = ColList(f"{i}", parent=self)
                self.TagsH.insertWidget(self.TagsH.count() - 1, column_list)
                self.TagsH.itemAt(self.TagsH.count() - 2).widget().loadList(self.db.columnsDistinct(col=i))
                column_list.selection_change.connect(self.numberOfElementsTextUpdate)

        self.label_numbe_of_elements.setText(f"Items: {self.db.find(count=True)[0]}")

    def getFiltersFromColumns(self):
        """
        Gets the selected values in each colList widget
        :return: dictionary
        """
        filters = {}
        for widget in self.scrollFilters.findChildren(ColList):
            if len(widget.SelectedItems()):
                filters[widget.title] = widget.SelectedItems()
        return filters

    def applyFilters(self):
        """
        Gets the selected values in each colList widget and filters out every item not containing these values
        """

        self.loadData(values=self.getFiltersFromColumns())
        self.numberOfElementsTextUpdate()

    def numberOfElementsTextUpdate(self):
        """
        Updates label_numbe_of_elements
        """
        self.label_numbe_of_elements.setText(
            f"Items: {self.db.find(values=self.getFiltersFromColumns(), count=True)[0]}")

    def loadData(self, values=None):
        """
        Places selected data from the database into a QTableWidget
        """
        self.tableWidget.clear()
        self.tableWidget.setRowCount(0)
        self.loadedData = []
        a = self.db.find(values, limit=100)
        for i in a:
            self.loadedData.append(Row(self.columns, i).row)
        for i in range(len(self.loadedData)):
            self.tableWidget.insertRow(i)
            for j in range(len(self.loadedData[i])):
                row = QtWidgets.QTableWidgetItem(str(self.loadedData[i][j]))
                self.tableWidget.setItem(i, j, row)
        # self.tableWidget.setModal(Table)

    def clearAllSelected(self):
        """
        Clears the selection to all ColList widgets
        """
        for widget in self.scrollFilters.findChildren(ColList):
            widget.clearSel()


class MainWindow(QtWidgets.QMainWindow):
    """
    Main application
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi("MainWindow.ui", self)

        self.dbviewer = SQLViewer()
        self.DatabaseLoc = None
        self.LoadData()

        if self.DatabaseLoc:
            self.db = DatabaseSQLite(self.DatabaseLoc[0])
            self.dbviewer.dbLink(self.db)
            self.dbviewer.loadTags()

        self.tab_Excerciese.addWidget(self.dbviewer)
        # Selected_tab
        self.ButtonPrint.clicked.connect(self.Print)

    def LoadData(self):
        """
        Loads variables
        """
        with open('objs.pkl', 'rb') as f:
            self.DatabaseLoc = pickle.load(f)

    def Print(self):
        """
        Opens print dialog
        """
        printer = QtPrintSupport.QPrinter()
        print_dialog = QtPrintSupport.QPrintDialog()
        if print_dialog.exec() == QtPrintSupport.QPrintDialog.accepted:
            self.handle_paint_request(printer)

    @staticmethod
    def SC():
        """
        Sanity check
        """
        print("working")


class DatabaseSQLite:
    """
    SQL implementation for Python. contains The following classes:
    Create, creates a database if one isn't present;
    Connect, opens database and runs function and arguments passed to it;
    CreateTable, creates a table in a given database;
    add, adds data to a table;
    readAll, (not recommended) returns tuple with all rows within the database;
    columnNames, returns list of columns within a table;
    columnsDistinct, gets distinct values for row in table.
    find, to do
    """

    def __init__(self, db_loc='', name='database.db'):
        self.defaultDBName = name
        self.defaultTable = "Material"
        self.dbPath = False
        self.Create(path=db_loc, name=name)

    def Create(self, path='', name=None):
        """
        Connects to a database in path, default is active file, named database.db. If
        Database does not exist it will be created
        :param path: (str) database folder's path, must be set according to OS
        :param name: (str) database name
        :return: True if database connection is valid
                 str if database connection Failed
        """
        if name is None:
            name = self.defaultDBName

        try:
            database = sqlite3.connect(path + name)
            print(sqlite3.version)
            if database:
                database.close()
                self.dbPath = path + name
                return True
        except Error as e:
            return e

    @staticmethod
    def RunCommand(c, inputs, *args):
        """

        :param c: SQLite curser
        :param inputs: SQL command
        :return: bool, depending if error found
        """

        c.execute(inputs, args)
        try:
            return 1
        except Error as e:
            return e

    def Connect(self, command, *args, save=False, **kwargs):
        """
        Input function, args and kwargs.
        print(db.Connect(db.RunCommand, sql_create_tasks_table))

        :param save:
        :param command: function
        :param args: passed function's arguments
        :param kwargs: passed function's keyword arguments
        :return: passed functions return or Error String

        example:
        Connect(self.RunCommand, SQL_command_string, save=True)
        """
        if isinstance(self.dbPath, str):
            try:
                database = sqlite3.connect(self.dbPath)
                curser = database.cursor()
                rt = True
                if callable(command):
                    command(curser, *args, **kwargs)
                    rt = curser.fetchall()
                    if save:
                        database.commit()
                if database:
                    database.close()
                    return rt

            except Error as e:
                return e

    def CreateTable(self, c, table=None, cols=None, types=None, adds=None):
        """

        Creates and sets up a table.

        :param c: SQLite curser
        :param table: (str) Name for the table
        :param cols: list(str) for name of columns
        :param types: list(str) informs SQL data type for columns
        :param adds: additional parameters

        example:
        print(db.Connect(db.CreateTable, "Material",
                   ["id", 'hyperlink', 'level', 'subject'],
                   ["integer", 'text', 'text', 'text'],
                   ["NOT NULL"]))
        """
        if table is None:
            table = self.defaultTable

        if (isinstance(cols, list)) & \
                (isinstance(types, list)) & \
                (isinstance(adds, list)):
            command_string = f'CREATE TABLE IF NOT EXISTS {table}(\n'
            for name, typ, add in list(itertools.zip_longest(cols, types, adds, fillvalue="")):
                command_string += f'{name} {typ} {add},\n'
            command_string = command_string[:-2] + ");"

            return self.RunCommand(c, command_string)

        else:
            return False

    def add(self, table=None, data=None):
        """
        Adds a row of data to database. All data must be in a dictionary
        :param table: (str) name of table
        :param data: (dict) dictionary with column_name : value
        :return: bool or error string

        example:
        db.add("Material", {"id": 2,
                              "hyperlink": "www.google.com",
                              "level": "C2",
                              "subject": "simple Present"})
        """
        if table is None:
            table = self.defaultTable

        if data:
            part1 = f"INSERT INTO {table}("
            part2 = f"VALUES("
            for col, val in zip(data.keys(), data.values()):
                part1 += f"'{col}', "
                part2 += f"'{val}', "

            command_string = part1[:-2] + ") " + part2[:-2] + ");"
            return self.Connect(self.RunCommand, command_string, save=True)

    def readAll(self, table=None, limit=None, offset=None):
        """

        :param table: (str) table name
        :param limit: (int) limits the number of results
        :param offset: (int) offsets the position sql starts listing
        :return: tuple of row in table

        example:
        db.readAll("Material")
        """
        if table is None:
            table = self.defaultTable

        cmd = f"SELECT * FROM {table}"

        if limit:
            cmd += f" LIMIT {limit}"
        if offset:
            cmd += f" OFFSET {offset}"
        return self.Connect(self.RunCommand, cmd)

    def columnNames(self, table=None):
        """
        Gets the name for each column in table
        :param table: (str) table name
        :return: list(str)

        example:
        print(db.columnNames())
        """
        if table is None:
            table = self.defaultTable
        a = self.Connect(self.RunCommand, f"select name from pragma_table_info('{table}')")
        return list(map(lambda x: x[0], a))

    def columnsDistinct(self, col="", table=None):
        """

        :param col: (str) column name
        :param table: (str) table name
        :return: tuple of (str)

        example:
        db.columnsDistinct("Material", "id")
        """
        if table is None:
            table = self.defaultTable

        result = self.Connect(self.RunCommand, f"SELECT DISTINCT  {col} FROM {table}")
        return [item for sublist in result for item in sublist]

    def find(self, values=None, table=None, selection='*', operation='AND', limit=None, offset=None, count=False):
        """
        Find rows with multiple values and or columns

        :param values: Dict{column: list(Values)}
        :param table: table in SQL database
        :param operation: SQL operation (AND, OR, ...) for columns
        :param selection: SQL select statement
        :param limit: (int) limits the number of results
        :param offset: (int) offsets the position sql starts listing

        Example:
        db.find(values={'Column_1': [1, 2, 3], 'Column_2': ["C2"]})
        SQLite command:
        SELECT * FROM TABLE_NAME WHERE Column_1 IN (?, ?, ?) AND Column_2 IN (?)
        """
        if table is None:
            table = self.defaultTable
        if values is None:
            values = {}

        if isinstance(values, dict):
            condition = ''
            for keys in values.keys():
                val = ', '.join("?" for value in values[keys])
                condition += f"{keys} IN ({val}) {operation} "
            query = f'SELECT {f"COUNT ({selection})" if count else f"{selection}"} FROM {table} ' \
                    f'{"WHERE" if values else ""} %s' % condition[:-4]

            if limit:
                query += f"LIMIT {limit}"
            if offset and not count:
                query += f" OFFSET {offset}"

            result = self.Connect(self.RunCommand, query,
                                  *[item for sublist in list(values.values()) for item in sublist])

            return result[0] if count else result


if __name__ == '__main__':

    """
    Generate dummy Data for database
    a = ["simple present", "Present Continuous", "Simple Past", "Past Continuous", "Present Perfect",
       "Present Perfect Continuous", "Simple Future"]
    for i in range(1000):
        j = db.add("Material", {"id": i,
                            "hyperlink": "www.google.com",
                            'level': f'{sample(["A", "B", "C"],1)[0]}{randint(1,2)}',
                            "subject": f"{sample(a, 1)[0]}"})                        
    """

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
