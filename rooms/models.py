from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser # Импорт для авторизации

# 1. Обновляем модель пользователя (Пункт 1 и 2 ТЗ)
class User(AbstractUser):
    # AbstractUser уже содержит: username, password, email, first_name, last_name
    # Нам остается только добавить имя, если username тебе недостаточно
    name = models.CharField(max_length=255, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

class Room(models.Model):
    name = models.CharField(max_length=255)
    qr_code = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Place(models.Model):
    STATUS_CHOICES = [
        ('free', 'Free'),
        ('occupied', 'Occupied'),
    ]

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='places')
    number = models.IntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='free')
    # Связываем с нашей новой моделью User
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    occupied_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('room', 'number')
        verbose_name = "Place"
        verbose_name_plural = "Places"

    def clean(self):
        if self.number < 1 or self.number > 10:
            raise ValidationError("Номер места должен быть от 1 до 10")
        if self.status == 'occupied' and not self.user:
            raise ValidationError("Занятое место должно иметь пользователя")
        if self.status == 'free' and (self.user or self.occupied_at):
            raise ValidationError("Свободное место не должно иметь пользователя")

    def __str__(self):
        return f"Room {self.room.id} - Place {self.number}"

# 2. Новая модель для истории и рейтинга (Пункт 3 ТЗ)
class OccupancyHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='booking_history')
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(auto_now_add=True) # Время выхода
    duration_minutes = models.IntegerField(default=0) # Итоговое время для рейтинга

    def save(self, *args, **kwargs):
        # Автоматически считаем минуты перед сохранением
        if self.start_time and self.end_time:
            diff = self.end_time - self.start_time
            self.duration_minutes = int(diff.total_seconds() // 60)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "History"
        verbose_name_plural = "Histories"