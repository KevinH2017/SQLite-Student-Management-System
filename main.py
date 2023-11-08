from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QGridLayout, \
    QLineEdit, QPushButton, QMainWindow, QTableWidget, QTableWidgetItem, \
        QDialog, QVBoxLayout, QComboBox, QToolBar, QStatusBar, QMessageBox
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt
import sys, sqlite3


class MainWindow(QMainWindow):
    """Shows window for Student Database System application"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Database System")
        self.setMinimumSize(420, 370)

        # Creates table, menu items, and widgets
        file_menu_item = self.menuBar().addMenu("&File")
        help_menu_item = self.menuBar().addMenu("&Help")
        edit_menu_item = self.menuBar().addMenu("&Edit")

        add_student = QAction(QIcon("./icons/add.png"), "Add Student", self)
        file_menu_item.addAction(add_student)
        add_student.triggered.connect(self.insert)  

        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)
        about_action.setMenuRole(QAction.MenuRole.NoRole)
        about_action.triggered.connect(self.about)

        search_action = QAction(QIcon("./icons/search.png"), "Search", self)
        edit_menu_item.addAction(search_action)
        search_action.triggered.connect(self.search)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("ID", "Name", "Course", "Mobile"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        # Create toolbar and add toolbar elements
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)
        toolbar.addAction(add_student)
        toolbar.addAction(search_action)

        # Create status bar and add status bar elements
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Detect a cell click
        self.table.cellClicked.connect(self.cell_clicked)

    def cell_clicked(self):
        """Adds Edit and Delete buttons when a cell is clicked"""
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)

        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)

        # Removes children widgets to avoid duplicates when clicking on cells
        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.status_bar.removeWidget(child)

        self.status_bar.addWidget(edit_button)
        self.status_bar.addWidget(delete_button)

    def load_data(self):
        """Gets data from database.db and puts it into rows and columns"""
        connection = sqlite3.connect("./database.db")
        result = connection.execute("SELECT * FROM students")
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

    def insert(self):
        dialog = InsertRecord()
        dialog.exec()

    def search(self):
        dialog = SearchRecord()
        dialog.exec()

    def edit(self):
        dialog = EditRecord()
        dialog.exec()

    def delete(self):
        dialog = DeleteRecord()
        dialog.exec()

    def about(self):
        dialog = AboutWindow()
        dialog.exec()


class AboutWindow(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        content = """
        This app was created during the course "The Python Mega Course".
        Feel free to modify and reuse this app.
        """
        self.setText(content)


class EditRecord(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Edit Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Get student name from selected row
        index = student_db.table.currentRow()
        student_name = student_db.table.item(index, 1).text()

        # Get id from selected row
        self.student_id = student_db.table.item(index, 0).text()

        # Add student name widget
        self.student_name = QLineEdit(student_name)
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Add courses combo box widget
        course_name = student_db.table.item(index, 2).text()
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(course_name)
        layout.addWidget(self.course_name)

        # Add phone number widget
        phone_number = student_db.table.item(index, 3).text()
        self.phone_number = QLineEdit(phone_number)
        self.phone_number.setPlaceholderText("Phone Number")
        layout.addWidget(self.phone_number)

        # Add submit button
        button = QPushButton("Update")
        button.clicked.connect(self.update_student)
        layout.addWidget(button)

        self.setLayout(layout)
 
    def update_student(self):
        connection = sqlite3.connect("./database.db")
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name=?, course=?, mobile=? WHERE id=?", 
        (self.student_name.text(), 
        self.course_name.itemText(self.course_name.currentIndex()), 
        self.phone_number.text(), 
        self.student_id))
        connection.commit()
        cursor.close()
        connection.close()
        
        # Refresh the table
        student_db.load_data()


class DeleteRecord(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete Student Data")

        layout = QGridLayout()
        confirmation = QLabel("Are you sure you want to delete?")
        yes = QPushButton("Yes")
        no = QPushButton("No")

        layout.addWidget(confirmation, 0, 0, 1, 2)
        layout.addWidget(yes, 1, 0)
        layout.addWidget(no, 1, 1)
        self.setLayout(layout)

        yes.clicked.connect(self.delete_student)

    def delete_student(self):
        # Get selected index and student id from selected row
        index = student_db.table.currentRow()
        student_id = student_db.table.item(index, 0).text()

        connection = sqlite3.connect("./database.db")
        cursor = connection.cursor()
        cursor.execute("DELETE from students WHERE id=?", (student_id, ))
        connection.commit()
        cursor.close()
        connection.close()
        student_db.load_data()

        self.close()

        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Success")
        confirmation_widget.setText("The record was deleted successfully!")
        confirmation_widget.exec()


class SearchRecord(QDialog):
    """Search dialog box for user to search for student's name"""
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
        """Searches database for student with inputed name"""
        name = self.student_name.text()
        connection = sqlite3.connect("./database.db")
        cursor = connection.cursor()
        result = cursor.execute("SELECT * FROM students WHERE name=?", (name,))
        rows = list(result)
        print(rows)
        items = student_db.table.findItems(name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            print(item)
            student_db.table.item(item.row(), 1).setSelected(True)

        cursor.close()
        connection.close()


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
        connection = sqlite3.connect("./database.db")
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