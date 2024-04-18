import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QListWidget,
    QMessageBox,
    QListWidgetItem,
)
import requests
import sqlite3


class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Weather App")
        self.setGeometry(100, 100, 400, 100)

        layout = QVBoxLayout()

        self.location_input = QLineEdit()
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_weather)
        layout.addWidget(QLabel("Enter location:"))
        layout.addWidget(self.location_input)
        layout.addWidget(self.search_button)

        self.history_list = QListWidget()
        self.history_button = QPushButton("Search History")
        self.history_button.clicked.connect(self.show_search_history)
        layout.addWidget(self.history_button)

        self.setLayout(layout)

        self.create_db_table()
        self.load_search_history()

    def create_db_table(self):
        conn = sqlite3.connect("weather_app.db")
        c = conn.cursor()
        c.execute(
            """CREATE TABLE IF NOT EXISTS search_history
                     (location text)"""
        )
        conn.commit()
        conn.close()

    def save_search_history(self, location):
        conn = sqlite3.connect("weather_app.db")
        c = conn.cursor()
        c.execute("INSERT INTO search_history VALUES (?)", (location,))
        conn.commit()
        conn.close()

    def load_search_history(self):
        conn = sqlite3.connect("weather_app.db")
        c = conn.cursor()
        c.execute("SELECT * FROM search_history")
        history = c.fetchall()
        conn.close()
        for item in history:
            self.history_list.addItem(item[0])

    def search_weather(self):
        location = self.location_input.text()
        url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid=f1f8d67b9fc8855b9848971b502dcee1&units=metric"
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200:
            weather_desc = data["weather"][0]["description"]
            temp = data["main"]["temp"]
            self.save_search_history(location)
            self.history_list.addItem(location)
            self.location_input.clear()
            self.show_weather_dialog(location, weather_desc, temp)
        else:
            error_message = data["message"]
            self.show_error_dialog(error_message)

    def show_weather_dialog(self, location, weather_desc, temp):
        msg = f"Weather in {location}: {weather_desc}, Temperature: {temp}°C"
        QMessageBox.information(self, "Weather Information", msg)

    def show_error_dialog(self, message):
        QMessageBox.critical(self, "Error", message)

    def show_search_history(self):
        self.history_window = SearchHistoryPage()
        self.history_window.show()


class SearchHistoryPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search History")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self.show_weather_from_history)
        layout.addWidget(QLabel("Search History:"))
        layout.addWidget(self.history_list)

        self.setLayout(layout)

        self.load_search_history()

    def load_search_history(self):
        conn = sqlite3.connect("weather_app.db")
        c = conn.cursor()
        c.execute("SELECT * FROM search_history")
        history = c.fetchall()
        conn.close()
        for item in history:
            location_item = QListWidgetItem(item[0])
            self.history_list.addItem(location_item)

    def show_weather_from_history(self, item):
        location = item.text()
        url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid=f1f8d67b9fc8855b9848971b502dcee1&units=metric"
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200:
            weather_desc = data["weather"][0]["description"]
            temp = data["main"]["temp"]
            self.show_weather_dialog(location, weather_desc, temp)
        else:
            error_message = data["message"]
            self.show_error_dialog(error_message)

    def show_weather_dialog(self, location, weather_desc, temp):
        msg = f"Weather in {location}: {weather_desc}, Temperature: {temp}°C"
        QMessageBox.information(self, "Weather Information", msg)

    def show_error_dialog(self, message):
        QMessageBox.critical(self, "Error", message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    weather_app = WeatherApp()
    weather_app.show()
    sys.exit(app.exec_())
