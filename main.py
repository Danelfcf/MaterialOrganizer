from PyQt6.QtWidgets import QApplication, QWidget
# Only needed for access to command line arguments
import sys
# Only to access database
from pymongo import MongoClient

class MainGUI:
    def __init__(self):
        # You need one (and only one) QApplication instance per application.
        # Pass in sys.argv to allow command line arguments for your app.
        # If you know you won't use command line arguments QApplication([]) works too.
        app = QApplication(sys.argv)

        print(self.connecttoDB())

        # Create a Qt widget, which will be our window.
        window = QWidget()
        window.show()  # IMPORTANT!!!!! Windows are hidden by default.

        # Start the event loop.
        app.exec()

    def connecttoDB(self):
        client = MongoClient('localhost', 27017)
        list_of_db = client.list_database_names()

        print(list_of_db)
        return client

# Your application won't reach here until you exit and the event
# loop has stopped.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    MainGUI()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
