from rest_framework import routers
from .views import WatchListViewSet, OfferViewSet, InventoryViewSet, ItemViewSet, UserCreateViewSet


router = routers.DefaultRouter()
router.register(r'watch-list', WatchListViewSet, basename='WatchList')
router.register(r'offers', OfferViewSet, basename='Offer')
router.register(r'inventory', InventoryViewSet, basename='Inventory')
router.register(r'items', ItemViewSet, basename='Item')
router.register(r'create-user', UserCreateViewSet)

urlpatterns = router.urls
