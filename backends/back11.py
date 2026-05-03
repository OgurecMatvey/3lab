import pandas as pd

class TourismBackend:
    def __init__(self):
        self.data = None
        self.yearly_totals = None
        self.window_title = "Анализ данных: Туристский поток (Вариант 11)"
        self.graph_title = "Туристский поток в России"
        self.data_label = "Фактический поток"

    #Получаем данные из файла
    def load_data(self, file_path):
        if file_path.endswith('.json'):
            self.data = pd.read_json(file_path)
        elif file_path.endswith('.xlsx'):
            self.data = pd.read_excel(file_path)
        else:
            raise ValueError("Данный формат файла не поддерживается")

        self.yearly_totals = self.data.groupby('Год')['Количество_туристов'].sum().reset_index()
        return self.data

    #Текст для вывода на график
    def info_text(self):
        if self.data is None:
            return None
        country_totals = self.data.groupby('Страна')['Количество_туристов'].sum()
        text = f"Максимум: {country_totals.idxmax()} ({country_totals.max()})\n"\
               f"Минимум: {country_totals.idxmin()} ({country_totals.min()})"
        return text

    #Метод для самого графика и прогноза
    def calculate_moving_average_and_forecast(self, period_n, forecast_years):
        if self.yearly_totals is None or len(self.yearly_totals) < period_n:
            return None

        #Данные для исходного графика
        years = list(self.yearly_totals['Год'])
        values = list(self.yearly_totals['Количество_туристов'])

        #Данные для прогноза
        forecast_years_list = []
        forecast_values = []


        current_window = values[-period_n:]
        last_year = years[-1]

        #Расчет прогноза
        for i in range(forecast_years):
            next_val = sum(current_window) / period_n
            forecast_years_list.append(last_year + i + 1)
            forecast_values.append(next_val)

            # Обновляем окно
            current_window.pop(0)
            current_window.append(next_val)

        return {
            'historical_years': years,
            'historical_values': values,
            'forecast_years': forecast_years_list,
            'forecast_values': forecast_values
        }