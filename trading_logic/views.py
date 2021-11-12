from django.contrib.auth import get_user_model
from django.db.models import F
from rest_framework.response import Response
from trading_logic.models import WatchList, Offer, Inventory, Item, UserWallet
from rest_framework import viewsets, permissions, status
from trading_logic.tasks import trade_task
from trading_logic.serializers import WatchListSerializer,\
    OfferSerializer, InventorySerializer,\
    ItemSerializer, UserCreateSerializer, UserWalletSerializer


class WatchListViewSet(viewsets.ModelViewSet):

    serializer_class = WatchListSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = WatchList.objects.all()


class OfferViewSet(viewsets.mixins.CreateModelMixin,
                   viewsets.mixins.UpdateModelMixin,
                   viewsets.mixins.DestroyModelMixin,
                   viewsets.mixins.ListModelMixin,
                   viewsets.GenericViewSet):

    serializer_class = OfferSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Offer.objects.all()
    trade_task.delay()

    def destroy(self, request, *args, **kwargs):
        offer_id = kwargs['pk']
        user = request.user

        if Offer.objects.filter(id=offer_id).get().order_type == 1:
            user_inventory = Inventory.objects.filter(user=user,
                                                      item=Offer.objects.filter(id=offer_id).get().item).get()
            user_inventory.quantity = F('quantity') + int(Offer.objects.filter(id=offer_id).get().quantity)
            user_inventory.save()
            Offer.objects.filter(id=offer_id).delete()

            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            user_wallet = UserWallet.objects.filter(user=user).get()
            user_wallet.money = F('money') + Offer.objects.filter(id=offer_id).get().price
            user_wallet.save()
            Offer.objects.filter(id=offer_id).delete()

            return Response(status=status.HTTP_204_NO_CONTENT)


class InventoryViewSet(viewsets.mixins.ListModelMixin, viewsets.GenericViewSet):

    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [permissions.IsAuthenticated]


class ItemViewSet(viewsets.mixins.ListModelMixin, viewsets.mixins.RetrieveModelMixin, viewsets.GenericViewSet):

    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    # permission_classes = [permissions.IsAuthenticated]


class UserCreateViewSet(viewsets.mixins.CreateModelMixin, viewsets.GenericViewSet):

    queryset = get_user_model().objects.all()
    serializer_class = UserCreateSerializer

    def retrieve(self):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserWalletViewSet(viewsets.mixins.RetrieveModelMixin, viewsets.GenericViewSet):

    queryset = UserWallet.objects.all()
    serializer_class = UserWalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        instance = UserWallet.objects.filter(user=user).get()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
