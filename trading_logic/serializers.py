from django.db import transaction
from trading_logic.models import WatchList, Offer, Inventory, Item, Currency, UserWallet
from rest_framework import serializers, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db.models import F


class UserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ['username']


class UserCreateSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = get_user_model()
        extra_kwargs = {'password': {'write_only': True}}
        fields = ['username', 'password']

    def create(self, validated_data):
        user = User(
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        UserWallet.objects.create(user=user.username, currency="USD", money=0.00)

        return user


class CurrencySerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Currency
        fields = ['code', 'name']


class ItemSerializer(serializers.ModelSerializer):
    currencies = CurrencySerializer(source='currency', allow_null=True)

    class Meta:
        model = Item
        fields = ['id', 'code', 'name', 'price', 'currencies', 'details']


class WatchListSerializer(serializers.ModelSerializer):
    items = ItemSerializer(allow_null=True, many=True, required=False, read_only=True)
    item_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = WatchList
        fields = ['id', 'items', 'item_id']
        depth = 1

    def create(self, validated_data):
        user = self.context['request'].user

        with transaction.atomic():
            instance = WatchList.objects.filter(user=user).first()
            if instance:
                WatchList.items.through.objects.create(
                    watchlist=instance, item_id=validated_data["item_id"])

            else:

                instance = WatchList.objects.create(user=user)
                WatchList.items.through.objects.create(watchlist=WatchList.objects.filter(user=user).first(),
                                                       item_id=validated_data["item_id"])

            return instance


class OfferSerializer(serializers.HyperlinkedModelSerializer):
    user = UserSerializer(read_only=True)
    item = ItemSerializer(allow_null=True, read_only=True)
    item_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Offer
        fields = ['id', 'user', 'item', 'order_type', 'entry_quantity', 'quantity', 'price', 'item_id']
        extra_kwargs = {'entry_quantity': {'write_only': True}, 'quantity': {'read_only': True}}

    def create(self, validated_data):
        user = self.context['request'].user

        with transaction.atomic():
            if int(getattr(Inventory.objects.filter(user=user, item_id=Item.objects.filter(
                    id=validated_data['item_id']).get()).get(),
                    'quantity')) >= validated_data['entry_quantity'] and validated_data['order_type'] == 1:

                offer = Offer.objects.create(user=user, item_id=validated_data['item_id'],
                                             entry_quantity=validated_data['entry_quantity'],
                                             quantity=validated_data['entry_quantity'],
                                             order_type=validated_data['order_type'],
                                             price=(float(getattr(Item.objects.filter(
                                                    id=validated_data['item_id']).get(), 'price'))) * validated_data[
                                                    'entry_quantity'])
                user_inventory = Inventory.objects.filter(user=user, item=Item.objects.filter(
                    id=validated_data['item_id']).get()).get()
                user_inventory.quantity = F('quantity') - int(validated_data['entry_quantity'])
                user_inventory.save()

                return offer

            elif validated_data['order_type'] == 2:
                offer = Offer.objects.create(user=user, item=Item.objects.filter(id=validated_data['item_id']).get(),
                                             entry_quantity=validated_data['entry_quantity'],
                                             quantity=validated_data['entry_quantity'],
                                             order_type=validated_data['order_type'],
                                             price=(float(getattr(Item.objects.filter(
                                                 id=validated_data['item_id']).get(), 'price'))) *
                                             validated_data['entry_quantity'])

                update_wallet = UserWallet.objects.filter(user=user).get()
                update_wallet.money = F('money') - (float(getattr(Item.objects.filter(id=
                                                                                      validated_data['item_id']).get(),
                                                                  'price')) * validated_data['entry_quantity'])
                update_wallet.save()

                return offer

            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)

    def update(self, instance, validated_data):
        user = self.context['request'].user
        offer_id = instance.id

        with transaction.atomic():

            delta_quantity = int(instance.entry_quantity) - int(validated_data['entry_quantity'])

            if instance.order_type == 1:

                if (int(Inventory.objects.filter(user=user, item=instance.item).get().quantity) + delta_quantity) >= 0:

                    instance.entry_quantity = validated_data['entry_quantity']
                    user_inventory = Inventory.objects.filter(user=user,
                                                              item=instance.item).get()
                    user_inventory.quantity = F('quantity') + delta_quantity
                    user_inventory.save()

                    instance.price = float(instance.price) - delta_quantity * float(
                        Item.objects.filter(id=Offer.objects.filter(id=offer_id).get().item.id).get().price)
                    instance.quantity = validated_data['entry_quantity']
                    instance.save()

                    return instance

                else:
                    return Response(status=status.HTTP_400_BAD_REQUEST)

            elif instance.order_type == 2:
                if (float(UserWallet.objects.filter(user=user).get().money) + delta_quantity * float(
                        instance.item.price)) >= 0:

                    instance.entry_quantity = validated_data['entry_quantity']
                    instance.price = float(instance.price) - delta_quantity * float(
                        Item.objects.filter(id=Offer.objects.filter(id=offer_id).get().item.id).get().price)
                    instance.quantity = validated_data['entry_quantity']
                    instance.save()

                    user_wallet = UserWallet.objects.filter(user=user).get()
                    user_wallet.money = F('money') + delta_quantity * float(
                        instance.item.price)
                    user_wallet.save()

                    return instance

                else:
                    return Response(status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)


class InventorySerializer(serializers.HyperlinkedModelSerializer):
    user = UserSerializer()
    items = ItemSerializer(allow_null=True)

    class Meta:
        model = Inventory
        fields = ['user', 'items', 'quantity']


class UserWalletSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserWallet
        fields = ['user', 'currency', 'money']
