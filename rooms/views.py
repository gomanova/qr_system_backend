from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, login
from django.db.models import Sum

from .models import Room, User, OccupancyHistory, Place
from .services import release_place, occupy_place_in_room, occupy_specific_place
from .serializers import PlaceSerializer, RoomPlacesSerializer

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email', '')
        name = request.data.get('name', '')

        if not username or not password:
            return Response({"success": False, "message": "Username и password обязательны"}, status=400)

        if User.objects.filter(username=username).exists():
            return Response({"success": False, "message": "Пользователь уже существует"}, status=400)

        user = User.objects.create_user(username=username, password=password, email=email, name=name)
        return Response({"success": True, "message": "Пользователь создан"}, status=201)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user:
            return Response({
                "success": True, 
                "user": {"id": user.id, "username": user.username, "name": user.name}
            })
        return Response({"success": False, "message": "Неверные данные"}, status=401)

class UserProfileView(APIView):

    def get(self, request):
        
        user_id = request.query_params.get('user_id') 
        try:
            user = User.objects.get(id=user_id)
            return Response({
                "id": user.id,
                "username": user.username,
                "name": user.name,
                "email": user.email,
                "date_joined": user.date_joined
            })
        except User.DoesNotExist:
            return Response({"message": "Пользователь не найден"}, status=404)

class LeaderboardView(APIView):
    def get(self, request):
        period = request.query_params.get('period', 'all')
        
        stats = OccupancyHistory.objects.values('user__username', 'user__name').annotate(
            total_time=Sum('duration_minutes')
        ).order_by('-total_time')[:10]

        return Response({
            "period": period,
            "leaders": stats
        })

class OccupySpecificPlaceView(APIView):
    """Пункт 4: Занять конкретное место по кнопке"""
    def post(self, request, place_id):
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({"message": "user_id обязателен"}, status=400)

        place, error = occupy_specific_place(user_id, place_id)
        if error:
            return Response({"success": False, "message": error}, status=400)

        return Response({"success": True, "place": PlaceSerializer(place).data})

class LeavePlaceView(APIView):
    def post(self, request, place_id):
        place, error = release_place(place_id)
        if error:
            return Response({"success": False, "message": error}, status=400)
        return Response({"success": True, "message": f"Место №{place.number} свободно"})

class EnterRoomView(APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        qr_code = request.data.get('qr_code')
        place, error = occupy_place_in_room(user_id, qr_code)
        if error: return Response({"success": False, "message": error}, status=400)
        return Response({"success": True, "place": PlaceSerializer(place).data})

class RoomPlacesView(APIView):
    def get(self, request, room_id):
        try:
            room = Room.objects.get(id=room_id)
            return Response(RoomPlacesSerializer(room).data)
        except Room.DoesNotExist:
            return Response({"message": "Комната не найдена"}, status=404)