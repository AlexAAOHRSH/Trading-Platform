from django.contrib.auth import get_user_model
from django.db.models import F
from rest_framework.response import Response
from trading_logic.models import WatchList, Offer, Inventory, Item, UserWallet
from rest_framework import viewsets, permissions, status
from trading_logic.tasks import trade_task
from trading_logic.serializers import WatchListSerializer,\
    OfferSerializer, InventorySerializer,\
    ItemSerializer, UserCreateSerializer, UserWalletSerializer


class WatchListViewSet(viewsets.mixins.RetrieveModelMixin, viewsets.mixins.CreateModelMixin,
                       viewsets.mixins.DestroyModelMixin, viewsets.GenericViewSet):

    serializer_class = WatchListSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = WatchList.objects.all()

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        instance = WatchList.objects.filter(user=user).get()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class OfferViewSet(viewsets.mixins.CreateModelMixin,
                   viewsets.mixins.UpdateModelMixin,
                   viewsets.mixins.DestroyModelMixin,
                   viewsets.mixins.ListModelMixin,
                   viewsets.GenericViewSet):

    serializer_class = OfferSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Offer.objects.all()
    trade_task.delay()


class InventoryViewSet(viewsets.mixins.RetrieveModelMixin, viewsets.GenericViewSet):

    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        instance = Inventory.objects.filter(user=user).get()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class ItemViewSet(viewsets.mixins.ListModelMixin, viewsets.mixins.RetrieveModelMixin, viewsets.GenericViewSet):

    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    # permission_classes = [permissions.IsAuthenticated]


class UserCreateViewSet(viewsets.mixins.CreateModelMixin, viewsets.mixins.RetrieveModelMixin, viewsets.GenericViewSet):

    queryset = get_user_model().objects.all()
    serializer_class = UserCreateSerializer


class UserWalletViewSet(viewsets.mixins.RetrieveModelMixin, viewsets.GenericViewSet):

    queryset = UserWallet.objects.all()
    serializer_class = UserWalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        instance = UserWallet.objects.filter(user=user).get()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
