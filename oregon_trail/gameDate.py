# Updates the date on the game header

from datetime import timedelta

class GameDate:
    def __init__(self, start_date): #start date must be input by the user
        self.current_date = start_date

    def advance_days(self, days):
        self.current_date += timedelta(days=days) #adds x number of days to the date

    def get_date(self):
        return self.current_date

