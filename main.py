import sqlite3

from PyQt5.QtWidgets import QWidget, QApplication, QListWidgetItem, QMessageBox
from PyQt5.uic import loadUi
#from qtconsole.qt import QtCore
from PyQt5.QtCore import Qt
import sys



#tasks = ["Write email", "Finish feature", "Watch tutorial"]

class Window(QWidget):
    def __init__(self):
        super(Window,self).__init__()
        loadUi("main.ui", self)
        self.calendarWidget.selectionChanged.connect(self.calendarDateChanged) # takvimin üzreine tıklandığında
        #self.updateTaskList()
        self.calendarDateChanged()
        self.saveButton.clicked.connect(self.saveChanges)
        self.addButton.clicked.connect(self.addNewTask)


    def calendarDateChanged(self):
        print("The calendar date was changed.")
        dateSelected = self.calendarWidget.selectedDate().toPyDate()# Takvimde hangi günü seçtiğinii
        print("Date selected:", dateSelected)
        # Date selected: PyQt5.QtCore.QDate(2025, 6, 12)
        # -> toPyDate() eklenir ve çıktı: Date selected: 2025-06-13
        # -> strftime("%m-%d") eklendi ve çıktı: Date selected: 06-27 # dataSelected = self.calendarWidget.selectedDate().toPyDate().strftime("%m-%d")
        # -> strftime("%Y") eklendi ve çıktı: Date selected: 2025 # dataSelected = self.calendarWidget.selectedDate().toPyDate().strftime("%Y")
        self.updateTaskList(dateSelected)

    def updateTaskList(self,date):
        """for task in tasks:
            # add them to the list widget
            item = QListWidgetItem(task)

            # Seçilir kutu yapımı ( check box)
            item.setFlags(item.flags()  |  Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)

            self.tasksListWidget.addItem(item)"""
        self.tasksListWidget.clear()

        db = sqlite3.connect("data.db")
        cursor = db.cursor()

        query = "SELECT task, completed FROM tasks WHERE date = ?"
        row = (date,)
        results = cursor.execute(query, row).fetchall()
        for result in results:
            item = QListWidgetItem(str(result[0]))
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            if result[1] == "YES":
                item.setCheckState(Qt.Checked)
            elif result[1] == "NO":
                item.setCheckState(Qt.Unchecked)
            self.tasksListWidget.addItem(item)
    def saveChanges(self):
        db = sqlite3.connect("data.db")
        cursor = db.cursor()
        date = self.calendarWidget.selectedDate().toPyDate()

        for i in range(self.tasksListWidget.count()):
            item = self.tasksListWidget.item(i)
            task = item.text()
            if item.checkState() == Qt.Checked:
                query = "UPDATE tasks SET completed = 'YES' WHERE task = ? AND date = ?"
            else:
                query = "UPDATE tasks SET completed = 'NO' WHERE task = ? AND date = ?"
            row = (task, date,)
            cursor.execute(query, row)
        db.commit()

        messageBox = QMessageBox()
        messageBox.setText("Changes saved.")
        messageBox.setStandardButtons(QMessageBox.Ok)
        messageBox.exec()

    def addNewTask(self):
        db = sqlite3.connect("data.db")
        cursor = db.cursor()

        newTask = str(self.taskLineEdit.text())
        date = self.calendarWidget.selectedDate().toPyDate()

        query = "INSERT INTO tasks(task, completed, date) VALUES (?,?,?)"
        row = (newTask, "NO", date,)

        cursor.execute(query, row)
        db.commit()
        self.updateTaskList(date)
        self.taskLineEdit.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())