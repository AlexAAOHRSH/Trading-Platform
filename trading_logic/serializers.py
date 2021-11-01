from .models import WatchList, Offer, Inventory, Item, Currency
from rest_framework import serializers
from django.contrib.auth.models import User


class UserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ['username']


class UserCreateSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        extra_kwargs = {'password': {'write_only': True}}
        fields = ['username', 'password', 'email']

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
        )

        user.set_password(validated_data['password'])
        user.save()

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
    items = ItemSerializer(allow_null=True, many=True, required=False)

    class Meta:
        model = WatchList
        fields = ['id', 'items']
        depth = 1


class OfferSerializer(serializers.HyperlinkedModelSerializer):
    items = ItemSerializer(source='item', allow_null=True)

    class Meta:
        model = Offer
        fields = ['id', 'items', 'order_type', 'entry_quantity', 'price']


class InventorySerializer(serializers.HyperlinkedModelSerializer):
    user = UserSerializer()
    items = ItemSerializer(source='item', allow_null=True)

    class Meta:
        model = Inventory
        fields = ['user', 'items', 'quantity']
