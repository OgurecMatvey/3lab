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
        else:
            raise ValueError("Данный формат файла не поддерживается")

        self.yearly_totals = self.data.groupby('Год')['Количество_туристов'].sum().reset_index()
        return self.data

