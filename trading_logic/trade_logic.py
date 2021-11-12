from trading_logic.models import Trade, Offer, Inventory, UserWallet
from django.db.models import F
from django.db import transaction


def create_trade(buy_offer, sell_offer):

    with transaction.atomic():
        if buy_offer.item.id == sell_offer.item.id:

            created_trade = Trade.objects.create(item=buy_offer.item, seller=buy_offer.user, buyer=buy_offer.user,
                                                 quantity=min(buy_offer.quantity, sell_offer.quantity),
                                                 unit_price=min(buy_offer.quantity, sell_offer.quantity)
                                                            * buy_offer.item.price,
                                                 buyer_offer=buy_offer, seller_offer=sell_offer)

            inventory, _ = Inventory.objects.get_or_create(user=buy_offer.user, item=buy_offer.item,
                                                           defaults={"quantity": 0})
            inventory.quantity += created_trade.quantity
            inventory.save()
            buy_offer.price = F('price') - created_trade.unit_price
            buy_offer.quantity = F('quantity') - created_trade.quantity
            buy_offer.save()
            sell_update_user_wallet = UserWallet.objects.filter(user=sell_offer.user).get()
            sell_update_user_wallet.money = F('money') + created_trade.unit_price
            sell_update_user_wallet.save()
            sell_offer.price = F('price') - created_trade.quantity
            sell_offer.quantity = F('quantity') - created_trade.quantity
            sell_offer.save()

            return created_trade
        else:
            raise RuntimeError(f"Item ids are not equal. {buy_offer.item.id} {buy_offer.item.name} and"
                               f" {sell_offer.item.id}"
                               f" {sell_offer.item.name}")


def run_trading(offer):
    first_offer = offer
    if first_offer.order_type == 1:
        order_type = 2
    else:
        order_type = 1

    offers = Offer.objects.filter(
        item=first_offer.item, order_type=order_type
    ).all()

    for offer in offers:

        with transaction.atomic():

            if first_offer.order_type != offer.order_type:

                if offer.order_type == 1:

                    create_trade(first_offer, offer)

                elif offer.order_type == 2:

                    create_trade(offer, first_offer)

                else:
                    raise RuntimeError("Not right order type. Most be 1 or 2")

            if offer.quantity == 0:
                offer.delete()
                offer.save()

            if first_offer.quantity == 0:
                first_offer.delete()
                first_offer.save()

