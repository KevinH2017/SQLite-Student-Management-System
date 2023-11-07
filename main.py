from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QGridLayout, \
    QLineEdit, QPushButton, QMainWindow, QTableWidget, QTableWidgetItem, \
        QDialog, QVBoxLayout, QComboBox
from PyQt6.QtGui import QAction
import sys, sqlite3


class MainWindow(QMainWindow):
    """Shows window for Student Database System application"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Database System")
        self.resize(420, 370)

        # Creates table, menu items, and widgets
        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")
        edit_menu_item = self.menuBar().addMenu("&Edit")

        add_student = QAction("Add Student", self)
        add_student.triggered.connect(self.insert)
        file_menu_item.addAction(add_student)

        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)
        about_action.setMenuRole(QAction.MenuRole.NoRole)

        search_action = QAction("Search", self)
        search_action.triggered.connect(self.search)
        edit_menu_item.addAction(search_action)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("ID", "Name", "Course", "Mobile"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

    def load_data(self):
        """Gets data from database.db and puts it into rows and columns"""
        connection = sqlite3.connect("./app13/database.db")
        result = connection.execute("SELECT * FROM students")
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

    def insert(self):
        """Allows user to insert new student information"""
        dialog = InsertRecord()
        dialog.exec()

    def search(self):
        dialog = SearchRecord()
        dialog.exec()


class SearchRecord(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Add student name widget
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Add submit button
        button = QPushButton("Search")
        button.clicked.connect(self.search_record)
        layout.addWidget(button)

        self.setLayout(layout)
        
    def search_record(self):
        pass


class InsertRecord(QDialog):
    """Adds new student's name, course, and phone number"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Add student name widget
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Add courses combo box widget
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        self.course_name.setPlaceholderText("Course Name")
        layout.addWidget(self.course_name)

        # Add phone number widget
        self.phone_number = QLineEdit()
        self.phone_number.setPlaceholderText("Phone Number")
        layout.addWidget(self.phone_number)

        # Add submit button
        button = QPushButton("Submit")
        button.clicked.connect(self.add_student)
        layout.addWidget(button)

        self.setLayout(layout)
        
    def add_student(self):
        """Adds data to students table in database.db"""
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        phone_num = self.phone_number.text()
        connection = sqlite3.connect("./app13/database.db")
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (name, course, mobile) VALUES (?,?,?)", (name, course, phone_num))

        connection.commit()
        cursor.close()
        connection.close()
        student_db.load_data()


# Executes MainWindow class
app = QApplication(sys.argv)
student_db = MainWindow()
student_db.show()
student_db.load_data()
sys.exit(app.exec())