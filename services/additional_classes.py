from datetime import datetime


class DateWindows:
    def __init__(self, date: str, windows: list[str], times: list[str]):
        self.date = date
        self.windows = windows
        self.times = times
    
    def get_available_windows(self):
        result = []
        for window in range(len(self.windows)):
            print(self.windows[window])
            if self.windows[window] == "":
                result.append(self.times[window])
        return result


class WorkerWindows:
    def __init__(self, worker_name: str, matrix: list[list[str]]):
        self.worker_name = worker_name
        self.matrix = matrix['values']
        self.times = self.matrix[0][1:]
        self.dates = {}

        for row in self.matrix[1:]:
            date = row[0]
            windows = row[1:]
            self.dates[date] = DateWindows(date, windows, self.times)
    
    def get_dates(self):
        result = []
        now = datetime.now()
        for date in self.dates.keys():
            if datetime.strptime(date, "%d.%m") < now:
                result.append(date)
        return result

    def get_windows(self, date: str):
        now = datetime.now()
        if datetime.strptime(date, "%d.%m") > now:
            print("Ya pidor")
            return []
        return self.dates[date].get_available_windows()



