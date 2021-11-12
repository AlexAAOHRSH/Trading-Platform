from decimal import Decimal
from django.core.validators import MinValueValidator
from django.db import models
from trading_logic.order_type import OrderType
from django.contrib.auth import get_user_model


User = get_user_model()


class Currency(models.Model):
    """Currency"""
    code = models.CharField("Code", max_length=8, unique=True)
    name = models.CharField("Name", max_length=128, unique=True)

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = "Currency"
        verbose_name_plural = "Currencies"


class UserWallet(models.Model):
    """User Wallet"""

    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    currency = models.ManyToManyField(Currency)
    money = models.DecimalField('Money', decimal_places=3, max_digits=100,
                                validators=[MinValueValidator(Decimal('0.000'))])

    def __str__(self):
        return f'{self.user} wallet'

    class Meta:
        verbose_name = "User Wallet"
        verbose_name_plural = "Users Wallets"


class Item(models.Model):
    """Particular stock"""
    code = models.CharField("Code", max_length=8, unique=True)
    name = models.CharField("Name", max_length=128, unique=True)
    price = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    currency = models.ForeignKey(Currency, related_name='currency', blank=True, null=True, on_delete=models.SET_NULL)
    details = models.TextField("Details", blank=True, null=True, max_length=512)

    def __str__(self):
        return f"{self.code} {self.id}"


class WatchList(models.Model):
    """List of favorite stocks"""
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    items = models.ManyToManyField(Item)

    def __str__(self):
        return f'{self.user} watch list'


class Price(models.Model):
    """Item prices"""
    currency = models.ForeignKey(Currency, blank=True, null=True, on_delete=models.SET_NULL)
    item = models.ForeignKey(Item, blank=True, null=True, on_delete=models.CASCADE, related_name='prices',
                             related_query_name='prices')
    price = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    date = models.DateTimeField(unique=True, blank=True, null=True)


class Offer(models.Model):
    """Request to buy or sell specific stocks"""
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    item = models.ForeignKey(Item, related_name='item', blank=True, null=True, on_delete=models.SET_NULL)
    entry_quantity = models.PositiveIntegerField("Requested quantity")
    quantity = models.PositiveIntegerField("Current quantity")
    __metaclass__ = OrderType
    order_type = models.PositiveSmallIntegerField(choices=OrderType.choices)
    price = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    is_active = models.BooleanField(default=True)


class Trade(models.Model):
    """Information about certain transaction"""
    item = models.ForeignKey(Item, blank=True, null=True, on_delete=models.SET_NULL)
    seller = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='seller_trade',
        related_query_name='seller_trade'
    )
    buyer = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='buyer_trade',
        related_query_name='buyer_trade'
    )
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=7, decimal_places=2)
    buyer_offer = models.ForeignKey(
        Offer,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='buyer_trade',
        related_query_name='buyer_trade'
    )
    seller_offer = models.ForeignKey(
        Offer,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='seller_trade',
        related_query_name='seller_trade'
    )


class Inventory(models.Model):
    """The number of stocks a particular user has"""
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    item = models.ForeignKey(Item, blank=True, null=True, on_delete=models.SET_NULL)
    quantity = models.PositiveIntegerField("Stocks quantity", default=0)

    class Meta:
        verbose_name = "Inventory"
        verbose_name_plural = "Inventory"
        unique_together = ('user', 'item',)

    def __str__(self):
        return f'{self.user} inventory {self.item}'
