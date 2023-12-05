# MainApp/models.py
from datetime import datetime

from django.db import models

class Candle(models.Model):
    id = models.AutoField(primary_key=True)
    open = models.DecimalField(max_digits=10, decimal_places=4)
    high = models.DecimalField(max_digits=10, decimal_places=4)
    low = models.DecimalField(max_digits=10, decimal_places=4)
    close = models.DecimalField(max_digits=10, decimal_places=4)
    date = models.DateField()

    # @classmethod
    # def create(cls, open, high, low, close, date_str):
    #     date = datetime.strptime(date_str, '%Y%m%d %H:%M')  # Adjust the format as needed
    #     return cls(open=open, high=high, low=low, close=close, date=date)