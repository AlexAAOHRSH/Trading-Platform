from django.contrib.auth.models import User
from django.db.models import F
from rest_framework.response import Response
from .models import WatchList, Offer, Inventory, Item
from rest_framework import viewsets, permissions, status
from .serializers import WatchListSerializer,\
    OfferSerializer, InventorySerializer,\
    ItemSerializer, UserCreateSerializer


class WatchListViewSet(viewsets.ModelViewSet):

    serializer_class = WatchListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        watch_list = WatchList.objects.all()
        return watch_list

    def create(self, request, *args, **kwargs):
        data = request.data
        user = request.user

        if WatchList.objects.filter(user=user).first():

            WatchList.items.through.objects.create(
                watchlist=WatchList.objects.filter(user=user).first(), item_id=data["items"])

        else:

            WatchList.objects.create(user=user)
            WatchList.items.through.objects.create(watchlist=WatchList.objects.filter(user=user).first(),
                                                   items=data["items"])

        serializer = WatchListSerializer(WatchList.objects.filter(user=user).first())

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        data = request.data
        user = request.user

        if WatchList.items.through.objects.filter(watchlist=WatchList.objects.filter(user=user).first(),
                                                  item_id=data["items"]).first():

            WatchList.items.through.objects.filter(watchlist=WatchList.objects.filter(user=user).first(),
                                                   item_id=data["items"]).first().delete()
            return Response(status=status.HTTP_200_OK)

        else:
            return Response(status=status.HTTP_204_NO_CONTENT)


class OfferViewSet(viewsets.mixins.CreateModelMixin,
                   viewsets.mixins.UpdateModelMixin,
                   viewsets.mixins.DestroyModelMixin,
                   viewsets.mixins.ListModelMixin,
                   viewsets.GenericViewSet):

    serializer_class = OfferSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        offer = Offer.objects.all()
        return offer

    def create(self, request, *args, **kwargs):
        data = request.data
        user = request.user

        if int(getattr(Inventory.objects.filter(user=user, item=Item.objects.filter(id=data['item']).get()).get(),
                       'quantity')) >= data['entry_quantity'] and data['order_type'] == 1:

            offer = Offer.objects.create(user=user, item=Item.objects.filter(id=data['item']).get(),
                                         entry_quantity=data['entry_quantity'],
                                         quantity=data['entry_quantity'], order_type=data['order_type'],
                                         price=(float(getattr(Item.objects.filter(id=data['item']).get(), 'price'))) *
                                         data['entry_quantity'])

            user_inventory = Inventory.objects.filter(user=user, item=Item.objects.filter(id=data['item']).get()).get()
            user_inventory.quantity = F('quantity') - int(data['entry_quantity'])
            user_inventory.save()

            serializer = OfferSerializer(offer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif data['order_type'] == 2:
            offer = Offer.objects.create(user=user, item=Item.objects.filter(id=data['item']).get(),
                                         entry_quantity=data['entry_quantity'],
                                         quantity=data['entry_quantity'], order_type=data['order_type'],
                                         price=(float(getattr(Item.objects.filter(id=data['item']).get(), 'price'))) *
                                         data['entry_quantity'])
            serializer = OfferSerializer(offer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        offer_id = kwargs['pk']
        user = request.user

        if Offer.objects.filter(id=offer_id).get().order_type == 1:
            user_inventory = Inventory.objects.filter(user=user,
                                                      item=Offer.objects.filter(id=offer_id).get().item).get()
            user_inventory.quantity = F('quantity') + int(Offer.objects.filter(id=offer_id).get().entry_quantity)
            user_inventory.save()
            Offer.objects.filter(id=offer_id).delete()

            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            Offer.objects.filter(id=offer_id).delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        user = request.user
        offer_id = kwargs['pk']
        patch_quantity = Offer.objects.filter(id=offer_id).get()
        delta_quantity = int(patch_quantity.entry_quantity) - int(request.data['entry_quantity'])

        if Offer.objects.filter(id=offer_id).get().order_type == 1:

            if (int(Inventory.objects.filter(user=user, item=Offer.objects.filter(
                    id=offer_id).get().item).get().quantity) + delta_quantity) >= 0:

                patch_quantity.entry_quantity = request.data['entry_quantity']
                patch_quantity.save()
                user_inventory = Inventory.objects.filter(user=user,
                                                          item=Offer.objects.filter(id=offer_id).get().item).get()
                user_inventory.quantity = F('quantity') + delta_quantity
                user_inventory.save()

                patch_price = Offer.objects.filter(id=offer_id).get()
                patch_price.price = float(patch_price.price) - delta_quantity*float(Item.objects.filter(id=Offer.objects.filter(id=offer_id).get().item.id).get().price)
                patch_price.save()

                return self.update(request, *args, **kwargs)

            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        else:

            patch_quantity = Offer.objects.filter(id=offer_id).get()
            patch_quantity.entry_quantity = request.data['entry_quantity']
            patch_quantity.save()

            patch_price = Offer.objects.filter(id=offer_id).get()
            patch_price.price = float(patch_price.price) - delta_quantity * float(
                Item.objects.filter(id=Offer.objects.filter(id=offer_id).get().item.id).get().price)
            patch_price.save()

            return self.update(request, *args, **kwargs)


class InventoryViewSet(viewsets.mixins.ListModelMixin, viewsets.GenericViewSet):

    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [permissions.IsAuthenticated]


class ItemViewSet(viewsets.mixins.ListModelMixin, viewsets.mixins.RetrieveModelMixin, viewsets.GenericViewSet):

    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserCreateViewSet(viewsets.mixins.CreateModelMixin, viewsets.GenericViewSet):

    queryset = User.objects.all()
    serializer_class = UserCreateSerializer

    def retrieve(self):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
