from django.urls import path
from .views import EnterRoomView, RoomPlacesView, LeavePlaceView

urlpatterns = [
    path('rooms/enter', EnterRoomView.as_view(), name='room-enter'),
    path('rooms/<int:room_id>/places', RoomPlacesView.as_view(), name='room-places'),
    path('places/<int:place_id>/leave', LeavePlaceView.as_view(), name='place-leave'), 
]