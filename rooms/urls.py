from django.urls import path
from .views import (
    # Старые
    EnterRoomView, 
    RoomPlacesView, 
    LeavePlaceView,
    # Новые
    RegisterView,
    LoginView,
    UserProfileView,
    LeaderboardView,
    OccupySpecificPlaceView
)

urlpatterns = [
    # Аутентификация
    path('auth/register', RegisterView.as_view(), name='register'),
    path('auth/login', LoginView.as_view(), name='login'),
    path('auth/me', UserProfileView.as_view(), name='user-profile'),
    
    # Места и комнаты
    path('rooms/enter', EnterRoomView.as_view(), name='room-enter'),
    path('rooms/<int:room_id>/places', RoomPlacesView.as_view(), name='room-places'),
    path('places/<int:place_id>/occupy', OccupySpecificPlaceView.as_view(), name='place-occupy'),
    path('places/<int:place_id>/leave', LeavePlaceView.as_view(), name='place-leave'), 
    
    # Статистика
    path('leaderboard', LeaderboardView.as_view(), name='leaderboard'),
]