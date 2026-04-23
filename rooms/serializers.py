from rest_framework import serializers
from .models import Place, Room

class PlaceSerializer(serializers.ModelSerializer):

    user_name = serializers.CharField(source='user.name', read_only=True, allow_null=True)

    class Meta:
        model = Place
        fields = ['id', 'number', 'status', 'user_name']

class RoomPlacesSerializer(serializers.ModelSerializer):
    
    places = PlaceSerializer(many=True, read_only=True) 

    class Meta:
        model = Room
        fields = ['id', 'name', 'places']