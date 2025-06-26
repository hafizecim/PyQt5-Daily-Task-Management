"""
============================================
 PyQt5 Daily Task Management Application
============================================

Bu uygulama, kullanıcıların günlük görevlerini takvim bazlı yönetmelerini sağlar.
Görev ekleme, tamamlama durumu güncelleme ve kayıtlı görevleri görüntüleme
işlevlerini SQLite veritabanı ile entegre olarak sunar.

Geliştirici: Hafizecim
Proje Tarihi: 2025

Not: Bu kod, PyQt5 kullanarak modern ve kullanıcı dostu masaüstü uygulamalar
geliştirmek isteyenler için örnek teşkil etmektedir.
"""

import sqlite3

from PyQt5.QtWidgets import QWidget, QApplication, QListWidgetItem, QMessageBox
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
import sys


class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()
        # UI dosyasını yükle
        loadUi("main.ui", self)

        # Takvim widget’ında tarih seçildiğinde calendarDateChanged fonksiyonu tetiklenecek
        self.calendarWidget.selectionChanged.connect(self.calendarDateChanged)

        # Başlangıçta seçili tarihe göre görev listesi güncelleniyor
        self.calendarDateChanged()

        # Kaydet butonuna tıklanınca saveChanges fonksiyonu çalışacak
        self.saveButton.clicked.connect(self.saveChanges)

        # Yeni görev ekle butonuna tıklanınca addNewTask fonksiyonu çalışacak
        self.addButton.clicked.connect(self.addNewTask)

    def calendarDateChanged(self):
        """Takvimde seçilen tarih değiştiğinde çağrılır."""
        print("The calendar date was changed.")

        # Takvimden seçili tarihi datetime.date formatında al
        dateSelected = self.calendarWidget.selectedDate().toPyDate()
        print("Date selected:", dateSelected)

        # Görev listesini seçilen tarihe göre güncelle
        self.updateTaskList(dateSelected)

    def updateTaskList(self, date):
        """Veritabanından seçilen tarihe ait görevleri çek ve listeye ekle."""
        # Listeyi temizle
        self.tasksListWidget.clear()

        # SQLite veritabanına bağlan
        db = sqlite3.connect("data.db")
        cursor = db.cursor()

        # Seçilen tarihe ait görevleri çek
        query = "SELECT task, completed FROM tasks WHERE date = ?"
        row = (date,)
        results = cursor.execute(query, row).fetchall()

        # Her görevi liste widget’ına ekle
        for result in results:
            item = QListWidgetItem(str(result[0]))

            # Her görev item’ı seçilebilir ve işaretlenebilir (check box)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)

            # Eğer görev tamamlandıysa işaretle, değilse boş bırak
            if result[1] == "YES":
                item.setCheckState(Qt.Checked)
            elif result[1] == "NO":
                item.setCheckState(Qt.Unchecked)

            self.tasksListWidget.addItem(item)

    def saveChanges(self):
        """Liste üzerinde işaretlenen görevlerin tamamlanma durumlarını veritabanına kaydet."""
        db = sqlite3.connect("data.db")
        cursor = db.cursor()

        # Takvimde seçili tarih
        date = self.calendarWidget.selectedDate().toPyDate()

        # Listedeki her görev için tamamlandı mı kontrol et ve veritabanını güncelle
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

        # Başarı mesajı göster
        messageBox = QMessageBox()
        messageBox.setText("Changes saved.")
        messageBox.setStandardButtons(QMessageBox.Ok)
        messageBox.exec()

    def addNewTask(self):
        """Yeni görev eklemek için veritabanına kayıt yap ve listeyi güncelle."""
        db = sqlite3.connect("data.db")
        cursor = db.cursor()

        # Kullanıcının girdiği yeni görev metni
        newTask = str(self.taskLineEdit.text())

        # Seçili tarih
        date = self.calendarWidget.selectedDate().toPyDate()

        # Veritabanına yeni görev ekle, varsayılan olarak tamamlanmamış (NO) durumda
        query = "INSERT INTO tasks(task, completed, date) VALUES (?,?,?)"
        row = (newTask, "NO", date,)

        cursor.execute(query, row)
        db.commit()

        # Listeyi güncelle ve metin kutusunu temizle
        self.updateTaskList(date)
        self.taskLineEdit.clear()


if __name__ == "__main__":
    # PyQt5 uygulamasını başlat
    app = QApplication(sys.argv)

    # Ana pencereyi oluştur ve göster
    window = Window()
    window.show()

    # Uygulamayı çalıştır ve kapatıldığında çık
    sys.exit(app.exec())
