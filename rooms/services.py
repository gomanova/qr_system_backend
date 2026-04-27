from django.db import transaction
from django.utils import timezone
from .models import Room, Place, User, OccupancyHistory

def release_place(place_id):
    """Освобождает место и записывает сессию в историю."""
    with transaction.atomic():
        try:
            
            place = Place.objects.select_for_update().get(id=place_id)
            
            if place.status == 'free':
                return None, "Место уже свободно"

            if place.user and place.occupied_at:
                OccupancyHistory.objects.create(
                    user=place.user,
                    place=place,
                    start_time=place.occupied_at
                )
            
            place.user = None
            place.status = 'free'
            place.occupied_at = None
            place.save()
            
            return place, None
        except Place.DoesNotExist:
            return None, "Место с таким ID не найдено"

def occupy_specific_place(user_id, place_id):
    """Ручное занятие конкретного места (Пункт 4 ТЗ)."""
    with transaction.atomic():
        try:
            user = User.objects.get(id=user_id)
            place = Place.objects.select_for_update().get(id=place_id)
            
            if place.status == 'occupied':
                return None, "Это место уже занято"
            
            if Place.objects.filter(user=user, status='occupied').exists():
                return None, "Вы уже занимаете другое место"

            place.user = user
            place.status = 'occupied'
            place.occupied_at = timezone.now()
            place.save()
            
            return place, None
        except (User.DoesNotExist, Place.DoesNotExist):
            return None, "Пользователь или место не найдены"

def occupy_place_in_room(user_id, qr_code):
    """Автоматическое занятие места (остается без изменений, работает как раньше)."""
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
    
    