"""
main for GUI project
"""

# Only to access database
from sqlitehandler import DatabaseSQLite
# Only needed for access to command line arguments
import sys
from Pages import SQLViewer

# Temporary imports
from PyQt6 import QtCore, QtWidgets, QtPrintSupport
from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QDialog, QSpinBox, QFileDialog, QComboBox
import pickle


class Preferences(QDialog):
    """
    pref window
    """

    def __init__(self, parent=None, db_loc=''):
        super().__init__(parent)
        # Load the GUI
        uic.loadUi("Preferences.ui", self)

        self.lineEdit_SQLDB_location.setText(db_loc)
        self.pushButton_sqlLocation.clicked.connect(self.SQLFileDialog)

    def SQLFileDialog(self):
        dialog = QFileDialog().getExistingDirectory()
        self.lineEdit_SQLDB_location.setText(dialog)
        print(dialog)

    @staticmethod
    def SC():
        print("working")


class MainWindow(QtWidgets.QMainWindow):
    """
    Main application
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi("MainWindow.ui", self)

        # Move checking for db location to another method in this class to clean main
        self.dbviewer = SQLViewer.SQLViewer()
        self.DatabaseLoc = None
        self.LoadData()

        if self.DatabaseLoc:
            self.db = DatabaseSQLite(self.DatabaseLoc)
            self.dbviewer.dbLink(self.db)
            self.dbviewer.loadTags()

        # keep all menu actions here in __init__
        self.actionPreferences.triggered.connect(self.Preferences)

        # this will be removed to another class
        self.tab_Excerciese.addWidget(self.dbviewer)
        # Selected_tab
        self.ButtonPrint.clicked.connect(self.Print)

    def LoadData(self):
        """
        Loads variables
        """
        with open('objs.pkl', 'rb') as f:
            self.DatabaseLoc = pickle.load(f)[0]

    def Preferences(self):
        """
        Opens Preferences popup
        """
        prefs = Preferences(db_loc=self.DatabaseLoc)
        if prefs.exec():
            self.DatabaseLoc = prefs.lineEdit_SQLDB_location.text()

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
