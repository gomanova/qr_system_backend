from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Room, Place


@receiver(post_save, sender=Room)
def create_places(sender, instance, created, **kwargs):
    if created:
        for i in range(1, 11):
            Place.objects.create(
                room=instance,
                number=i
            )



