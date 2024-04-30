from django.conf import settings
from django.db import models
from django.contrib.auth.models import User, AbstractUser
from PIL import Image


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        Profile.objects.get_or_create(user=self)

    def __str__(self):
        return self.email


# Extending User Model Using a One-To-One Link
class Profile(models.Model):
    # objects = Profile()
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # email = models.EmailField(unique=True)
    # objects = models.Manager()  # Explicitly define the objects manager
    avatar = models.ImageField(default='default.jpg', upload_to='profile_images')
    bio = models.TextField()

    # balance = models.DecimalField(default=1000, max_digits=10, decimal_places=2)
    # currency_choices = [('GBP', 'British Pound'), ('USD', 'US Dollar'), ('EUR', 'Euro')]
    # default_currency = 'GBP'  # Choose your default currency here
    # currency = models.CharField(max_length=3, choices=currency_choices, default=default_currency)

    def __str__(self):
        return self.user.username

    # resizing images
    def save(self, *args, **kwargs):
        super().save()

        img = Image.open(self.avatar.path)

        if img.height > 100 or img.width > 100:
            new_img = (100, 100)
            img.thumbnail(new_img)
            img.save(self.avatar.path)


class Account(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    balance = models.DecimalField(default=1000, max_digits=10, decimal_places=2)
    currency_choices = [('GBP', 'British Pound'), ('USD', 'US Dollar'), ('EUR', 'Euro')]
    default_currency = 'GBP'  # Choose your default currency here
    currency = models.CharField(max_length=3, choices=currency_choices, default=default_currency)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username}"
