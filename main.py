import sys
from PyQt6.QtWidgets import (QMainWindow, QApplication, QPushButton, QVBoxLayout,
                             QHBoxLayout, QWidget, QTableWidget, QTableWidgetItem,
                             QFileDialog, QSpinBox, QLabel, QComboBox)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from backends import back11, back17


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.resize(1000, 700)
        self.data = None
        self.backend = back11.TourismBackend()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        """
        Там где Back17.TourismBackend() замени на название своего класса
        """
        self.backends = {
            "Вариант 17 (Рождаемость)": back17.TourismBackend(),
            "Вариант 11 (Туризм)": back11.TourismBackend()
        }

        # Устанавливаем бэкенд по умолчанию
        self.current_backend = self.backends["Вариант 17 (Рождаемость)"]

        # --- Добавляем выпадающий список в интерфейс ---
        self.variant_selector = QComboBox()
        self.variant_selector.addItems(self.backends.keys())
        self.variant_selector.currentTextChanged.connect(self.change_variant)


        # Устанавливаем начальный заголовок окна
        self.setWindowTitle(self.current_backend.window_title)

        controls_layout = QVBoxLayout()
        controls_layout.insertWidget(0, self.variant_selector)
        self.btn_load = QPushButton("Загрузить данные (CSV/JSON)")
        self.btn_load.clicked.connect(self.load_file)

        self.label_n = QLabel("Период скользящей средней (N):")
        self.n_input = QSpinBox()
        self.n_input.setRange(2, 10)
        self.n_input.setValue(3)

        self.btn_calc = QPushButton("Построить и рассчитать")
        self.btn_calc.setEnabled(False)
        self.btn_calc.clicked.connect(self.update_view)

        self.btn_export = QPushButton("Экспортировать график")
        self.btn_export.clicked.connect(self.export_plot)

        self.table = QTableWidget()
        controls_layout.addWidget(self.btn_load)
        controls_layout.addWidget(self.label_n)
        controls_layout.addWidget(self.n_input)
        controls_layout.addWidget(self.btn_calc)
        controls_layout.addWidget(self.btn_export)
        controls_layout.addWidget(self.table)

        plot_layout = QVBoxLayout()
        self.canvas = MplCanvas(self, width=7, height=6, dpi=100)
        self.toolbar = NavigationToolbar(self.canvas, self)
        plot_layout.addWidget(self.toolbar)
        plot_layout.addWidget(self.canvas)

        main_layout.addLayout(controls_layout, 1)
        main_layout.addLayout(plot_layout, 2)

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Открыть файл", "", "Data Files (*.csv *.json *.xlsx)")
        if file_path:
            try:

                self.data = self.backend.load_data(file_path)
                self.fill_table()


                self.btn_calc.setEnabled(True)
            except Exception as e:
                print(f"Ошибка загрузки файла: {e}")

    def fill_table(self):
        self.table.setRowCount(len(self.data))
        self.table.setColumnCount(len(self.data.columns))
        self.table.setHorizontalHeaderLabels(self.data.columns)
        for i in range(len(self.data)):
            for j in range(len(self.data.columns)):
                self.table.setItem(i, j, QTableWidgetItem(str(self.data.iloc[i, j])))

    def update_view(self):
        self.canvas.axes.cla()
        n = self.n_input.value()

        results = self.backend.calculate_moving_average_and_forecast(period_n=n, forecast_years=3)

        if results:
            self.canvas.axes.plot(results['historical_years'], results['historical_values'], 'o-',
                                  label=self.current_backend.data_label, color='blue')

            forecast_x = [results['historical_years'][-1]] + results['forecast_years']
            forecast_y = [results['historical_values'][-1]] + results['forecast_values']
            self.canvas.axes.plot(forecast_x, forecast_y, 'r--x', label='Прогноз')

            if self.backend.info_text():

                self.canvas.axes.text(0.05, 0.90, self.backend.info_text(),
                                      transform=self.canvas.axes.transAxes,
                                      fontsize=10, verticalalignment='top',
                                      bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8,
                                                edgecolor='gray'))
        self.canvas.axes.set_title(self.current_backend.graph_title)
        self.canvas.axes.legend()
        self.canvas.axes.grid(True)
        self.canvas.draw()

    def export_plot(self):
        file_path, _ = QFileDialog.getSaveFileName(self,"Сохранить график", "", "PNG (*.png);;PDF (*.pdf)")
        if file_path:
            self.canvas.figure.savefig(file_path)

    def change_variant(self, variant_name):
        self.current_backend = self.backends[variant_name]
        self.setWindowTitle(self.current_backend.window_title)

        self.table.setRowCount(0)
        self.canvas.axes.cla()
        self.canvas.draw()
        self.btn_calc.setEnabled(False)

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())