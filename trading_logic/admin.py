from django.contrib import admin
from trading_logic.models import Currency, Item, WatchList, Inventory,\
    Trade, Offer, Price, UserWallet

admin.site.register(Currency)
admin.site.register(Item)
admin.site.register(WatchList)
admin.site.register(Inventory)
admin.site.register(Trade)
admin.site.register(Offer)
admin.site.register(Price)
admin.site.register(UserWallet)
