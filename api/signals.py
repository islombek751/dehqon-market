from api.models import User,Profile
from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    print(created)
    if created:
        Profile.objects.create(user=instance)


@receiver(post_delete, sender=Profile)
def delete_user_profile(sender, instance, **kwargs):
    if instance.user:
        user = User.objects.get(username=instance.user.username)
        user.delete()
        