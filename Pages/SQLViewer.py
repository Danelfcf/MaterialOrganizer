from PyQt6 import QtCore, QtWidgets, QtPrintSupport
from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QDialog, QSpinBox, QFileDialog, QComboBox


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
        if __name__ == "__main__":
            uic.loadUi("..//Listwidget.ui", self)
        else:
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

    @staticmethod
    def UserSelectionChange():
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

    def __init__(self, parent=None, file="SQLViewer.ui"):
        super().__init__(parent)
        # Load the GUI
        uic.loadUi(file, self)

        self.ConfigureWidgets()
        self.SetupSignalConnections()

        self.db = False
        self.columns = None
        self.loadedData = False

        self.update()

    def ConfigureWidgets(self):
        """
        Configure loaded widgets
        """
        self.scrollFilters.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # trying to enable drag and drop
        self.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.tableWidget.setDragEnabled(True)
        self.tableWidget.viewport().setAcceptDrops(True)
        self.tableWidget.setDropIndicatorShown(True)
        self.tableWidget.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.InternalMove)

    def SetupSignalConnections(self):
        """
        Sets up Signal handling for GUI
        """
        # Filters Area
        self.ButtonClearAll.clicked.connect(self.clearAllSelected)
        self.ButtonApply.clicked.connect(self.applyFilters)
        self.comboBox_databases.currentTextChanged.connect(self.dataBaseSelectionBox)

        # TableWidgetArea

        # Page selection area at the foot of page
        self.spinBox_page.valueChanged.connect(self.pageChange)
        self.comboBox_data_depth.currentIndexChanged.connect(lambda: self.loadData(values=self.getFiltersFromColumns()))

    def dbLink(self, x):
        """
        Receives a Database class for program to access and control
        :param x: Database class
        """
        self.db = x
        self.columns = self.db.columnNames()
        self.tableWidget.setColumnCount(len(self.columns))
        self.tableWidget.setHorizontalHeaderLabels(self.columns)
        self.comboBox_databases.addItems(self.db.Existence())
        self.loadData()

    def dataBaseSelectionBox(self):
        print("ad")

    def setPages(self):
        """
        page counter logic
        """
        max_pages = round(0.5 + self.db.find(values=self.getFiltersFromColumns(), count=True)[0]
                          / int(self.comboBox_data_depth.currentText()))
        self.label_number_of_pages.setText(f"{max_pages}")
        self.spinBox_page.setMaximum(max_pages)
        self.spinBox_page.setValue(0)

    def pageChange(self):
        """
        Handles value change for page spinbox
        """
        self.loadData(values=self.getFiltersFromColumns())

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

        self.numberOfElementsTextUpdate()
        self.setPages()

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
        self.setPages()

    def numberOfElementsTextUpdate(self):
        """
        Updates label_number_of_elements
        """
        self.label_number_of_elements.setText(
            f"Items: {self.db.find(values=self.getFiltersFromColumns(), count=True)[0]}")

    def loadData(self, values=None):
        """
        Places selected data from the database into a QTableWidget
        """
        self.tableWidget.clear()
        self.tableWidget.setRowCount(0)
        self.loadedData = []
        a = self.db.find(values, limit=int(self.comboBox_data_depth.currentText()),
                         offset=self.spinBox_page.value() * int(self.comboBox_data_depth.currentText()))
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


if __name__ == "__main__":
    import sys
    # Only to access database
    from sqlitehandler import DatabaseSQLite

    db = DatabaseSQLite()

    print("Running SQLite3 viewer Independently")
    app = QtWidgets.QApplication(sys.argv)
    window = SQLViewer(file="..//SQLViewer.ui")
    window.dbLink(db)
    window.loadTags()
    window.show()
    app.exec()
