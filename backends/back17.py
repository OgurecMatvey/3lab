import pandas as pd
import numpy as np


class BirthRateBackend:
    def __init__(self):
        self.data = None
        self.window_title = "Анализ: Рожденные вне брака (Вариант 17)"
        self.graph_title = "Процент детей, рожденных вне брака"
        self.data_label = "Исторические данные (%)"

    def load_data(self, file_path):
        """
        Загрузка данных. Ожидаются колонки: 'Год' и 'Процент'.
        """
        if file_path.endswith('.csv'):
            self.data = pd.read_csv(file_path)
        elif file_path.endswith('.json'):
            self.data = pd.read_json(file_path)
        elif file_path.endswith('.xlsx'):
            self.data = pd.read_excel(file_path)
        else:
            raise ValueError("Формат файла не поддерживается")

        # Сортируем по году, чтобы расчеты были корректными
        self.data = self.data.sort_values('Год')
        return self.data

    def info_text(self):
        """
        Вычисляет максимальный и минимальный процент изменения данных за год.
        """
        if self.data is None or len(self.data) < 2:
            return None

        # Вычисляем разницу между текущим и предыдущим годом
        # .diff() считает: значение_текущее - значение_предыдущее
        changes = self.data['Процент'].diff().dropna()

        max_ch = changes.max()
        min_ch = changes.min()

        text = (f"Макс. изменение за год: {max_ch:+.2f}%\n"
                f"Мин. изменение за год: {min_ch:+.2f}%")
        return text

    def calculate_moving_average_and_forecast(self, period_n, forecast_years):
        """
        Рассчитывает скользящую среднюю и делает экстраполяцию.
        """
        if self.data is None or len(self.data) < period_n:
            return None

        years = self.data['Год'].tolist()
        values = self.data['Процент'].tolist()

        # 1. Расчет исторической скользящей средней (MA)
        ma_values = [None] * (period_n - 1)
        for i in range(period_n, len(values) + 1):
            window = values[i - period_n: i]
            ma_values.append(sum(window) / period_n)

        # 2. Экстраполяция (Прогноз)
        # Начинаем с последних известных данных
        current_window = values[-period_n:]
        forecast_years_list = []
        forecast_values = []
        last_year = years[-1]

        for i in range(1, forecast_years + 1):
            # Новая точка — это среднее значение предыдущего окна
            next_val = sum(current_window) / period_n
            forecast_years_list.append(last_year + i)
            forecast_values.append(next_val)

            # Сдвигаем окно: убираем первое, добавляем только что предсказанное
            current_window.pop(0)
            current_window.append(next_val)

        return {
            'historical_years': years,
            'historical_values': values,
            'historical_ma': ma_values,
            'forecast_years': forecast_years_list,
            'forecast_values': forecast_values
        }