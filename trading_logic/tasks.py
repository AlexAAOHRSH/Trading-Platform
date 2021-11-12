from trading_platform import celery_app
from trading_logic.models import Offer
from trading_logic.trade_logic import run_trading


@celery_app.task()
def trade_task():
    for offer in Offer.objects.filter(order_type=1):
        run_trading(offer)
