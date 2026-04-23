from django.db import transaction
from django.utils import timezone
from .models import Room, Place, User

def release_place(place_id):
    try:
        place = Place.objects.get(id=place_id)
        if place.status == 'free':
            return None, "Место уже свободно"
        
        place.user = None
        place.status = 'free'
        place.occupied_at = None
        place.save()
        
        return place, None
    except Place.DoesNotExist:
        return None, "Место с таким ID не найдено"
    
def occupy_place_in_room(user_id, qr_code):
    try:
        if not User.objects.filter(id=user_id).exists():
            return None, f"Пользователь с ID {user_id} не найден"

        try:
            room = Room.objects.get(qr_code=qr_code)
        except Room.DoesNotExist:
            return None, "Комната не найдена"

        existing_place = Place.objects.filter(room=room, user_id=user_id).first()
        if existing_place:
            return existing_place, None

        with transaction.atomic():
            place = Place.objects.filter(
                room=room, 
                user__isnull=True,
                status='free'
            ).order_by('number').select_for_update().first()

            if not place:
                return None, "Свободных мест нет"
            place.user_id = user_id 
            place.status = 'occupied'
            place.occupied_at = timezone.now()
            place.save()

            return place, None

    except Exception as e:
        return None, f"Ошибка сервера: {str(e)}"
    
    