import sys

from PyQt5 import QtWidgets

from clases import Mantenimiento


def main():
    app = QtWidgets.QApplication(sys.argv)  # A new instance of QApplication
    progr = Mantenimiento()  # We set the form to be our ExampleApp (design)
    progr.show()  # Show the GUI
    app.exec_()  # and execute the app


if __name__ == '__main__':  # if we're running file directly and not importing it
    main()  # run the main function
