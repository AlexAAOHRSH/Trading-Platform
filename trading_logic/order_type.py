from django.db import models


class OrderType(models.IntegerChoices):
    SELL = 1
    BUY = 2
