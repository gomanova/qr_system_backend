from django.shortcuts import render
from .services import release_place, occupy_place_in_room
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import PlaceSerializer, RoomPlacesSerializer
from .models import Room


class LeavePlaceView(APIView):
    def post(self, request, place_id):
        place, error = release_place(place_id)
        
        if error:
            return Response({"success": False, "message": error}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            "success": True, 
            "message": f"Место №{place.number} теперь свободно"
        })

class EnterRoomView(APIView):
    """Вход в комнату по QR"""
    def post(self, request):
        user_id = request.data.get('user_id')
        qr_code = request.data.get('qr_code')

        if not user_id or not qr_code:
            return Response({"success": False, "message": "user_id и qr_code обязательны"}, status=400)

        place, error = occupy_place_in_room(user_id, qr_code)

        if error:
            return Response({"success": False, "message": error}, status=400)

        serializer = PlaceSerializer(place)
        return Response({
            "success": True,
            "room_id": place.room.id,
            "place": serializer.data
        })

class RoomPlacesView(APIView):
    def get(self, request, room_id):
        try:
            room = Room.objects.get(id=room_id)
            serializer = RoomPlacesSerializer(room)
            return Response(serializer.data)
        except Room.DoesNotExist:
            return Response({"message": "Комната не найдена"}, status=404)