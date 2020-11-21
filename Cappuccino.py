import sqlite3
import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMessageBox, QDialog
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem
import datetime as dt


class MyDialog(QDialog):
    def __init__(self, array, changed=False):
        super().__init__()
        uic.loadUi('UI/addEditCoffeeForm.ui', self)
        self.pushButton.clicked.connect(self.accept_data)
        if changed:
            self.setWindowTitle('Редактирование записи')
            self.lineEdit.setText(str(array[1]))
            self.lineEdit_2.setText(str(array[2]))
            self.lineEdit_3.setText(str(array[3]))
            self.lineEdit_4.setText(str(array[4]))
            self.lineEdit_5.setText(str(array[5]))
            self.lineEdit_6.setText(str(array[6]))
        else:
            self.setWindowTitle('Добавить элемент')
        self.arr = []

    def accept_data(self):
        title = self.lineEdit.text()
        degree = self.lineEdit_2.text()
        ground = self.lineEdit_3.text()
        description = self.lineEdit_4.text()
        price = self.lineEdit_5.text()
        volume = self.lineEdit_6.text()
        try:
            if title:
                self.arr = [title, degree, ground, description, price, volume]
                self.close()
            else:
                self.label_12.setText('Неверно заполнена форма')
                return
        except Exception:
            self.label_12.setText('Неверно заполнена форма')
            return
        self.close()

    def get_items(self):
        return self.arr


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("UI/UI_cappuccino.ui", self)
        self.con = sqlite3.connect("data/coffee.db")
        self.setWindowTitle("Фильмотека")
        self.pushButton_2.clicked.connect(self.change_film)
        self.pushButton_3.clicked.connect(self.add_film)
        self.update_films()

    def add_film(self):
        mdf = MyDialog([], False)
        mdf.show()
        mdf.exec_()
        data = mdf.get_items()
        if data:
            max_id = self.con.execute("""select max(id) from coffee""").fetchone()[0]
            cur = self.con.cursor()
            cur.execute("""INSERT INTO coffee(id, 
            title, degree, ground, description, price, volume) VALUES(?, ?, ?, ?, ?, ?, ?)""", (
                max_id + 1, *[x for x in data]))
            self.con.commit()
            self.update_films()

    def change_film(self):
        cur = self.con.cursor()
        rows = list(
            set([i.row() for i in self.tableWidget.selectedItems()]))
        ids = [self.tableWidget.item(i, 0).text() for i in rows]
        if not ids:
            self.statusBar().showMessage('Записть не выделена')
            return
        elif len(ids) > 1:
            self.statusBar().showMessage('Выбрано более 1 записи')
            return
        item_inf = cur.execute(
            "SELECT * FROM coffee WHERE id IN (" + ", ".join(
                '?' * len(ids)) + ")", ids).fetchone()
        mdf = MyDialog(item_inf, True)
        mdf.show()
        mdf.exec_()
        data = mdf.get_items()
        if data:
            id = item_inf[0][0]
            cur.execute('''UPDATE coffee 
                           SET  title = ?, degree = ?, ground = ?, description = ?,
                           price = ?, volume = ?
                           where id LIKE ?''',
                        (data[0], data[1], data[2], data[3], int(data[4]), float(data[5]), int(id)))
            self.con.commit()
            self.update_films()

    def update_films(self):
        cur = self.con.cursor()
        result = cur.execute("""SELECT * FROM coffee""").fetchall()
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setRowCount(0)
        self.tableWidget.setHorizontalHeaderLabels(['id', 'title', 'degree', 'ground', 'description',
                                                    'price', 'volume'])
        for i, row in enumerate(result):
            self.tableWidget.setRowCount(
                self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tableWidget.setItem(
                    i, j, QTableWidgetItem(str(elem)))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec())
