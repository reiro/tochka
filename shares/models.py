import datetime

from django.db import models
from django.utils import timezone


class Share(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class TradeEvent(models.Model):
    share = models.ForeignKey(Share, on_delete=models.CASCADE)
    date = models.DateField()
    volume = models.IntegerField(default=0)
    open_value = models.FloatField(default=0.)
    high_value = models.FloatField(default=0.)
    low_value = models.FloatField(default=0.)
    close_value = models.FloatField(default=0.)

    def __str__(self):
        return "{}: {} - Volume: {}".format(self.share.name, self.date, self.volume)

class Insider(models.Model):
    name = models.CharField(max_length=200)
    relation = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class InsiderTradeEvent(models.Model):
    insider = models.ForeignKey(Insider, on_delete=models.CASCADE)
    share = models.ForeignKey(Share, on_delete=models.CASCADE)
    date = models.DateField()
    transaction_type = models.CharField(max_length=200)
    owner_type = models.CharField(max_length=200)
    shares_traded = models.IntegerField(default=0)
    shares_held = models.IntegerField(default=0)
    last_price = models.FloatField(default=0.)

    def __str__(self):
        return str(self.id)
