from rest_framework import routers
from trading_logic.views import WatchListViewSet, OfferViewSet, InventoryViewSet, ItemViewSet, UserCreateViewSet, \
     UserWalletViewSet


router = routers.DefaultRouter()
router.register(r'watch-list', WatchListViewSet, basename='WatchList')
router.register(r'offers', OfferViewSet, basename='Offer')
router.register(r'inventory', InventoryViewSet, basename='Inventory')
router.register(r'items', ItemViewSet, basename='Item')
router.register(r'user-wallet', UserWalletViewSet, basename='UserWallet')
router.register(r'create-user', UserCreateViewSet)

urlpatterns = router.urls
