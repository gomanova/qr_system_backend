from django.db import models
from django.core.exceptions import ValidationError


class User(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


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
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    occupied_at = models.DateTimeField(null=True, blank=True)


    class Meta:
        unique_together = ('room', 'number')
        indexes = [
            models.Index(fields=['room', 'status']),
        ]
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
        return f"{self.room.name} - Place {self.number}"
