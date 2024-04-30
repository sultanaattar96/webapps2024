from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from register.models import Account, Profile


class Transaction(models.Model):
    sender = models.ForeignKey(Account, related_name='sent_transactions', on_delete=models.CASCADE)
    recipient_email = models.EmailField()  # Field to store recipient's email address
    recipient = models.ForeignKey(Account, related_name='received_transactions', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency_choices = [('GBP', 'British Pound'), ('USD', 'US Dollar'), ('EUR', 'Euro')]
    currency = models.CharField(max_length=3, choices=currency_choices)
    timestamp = models.DateTimeField(auto_now_add=False)
    is_request = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('SUCCESS', 'Success'),
    ]
    # if it is normal transaction just set as Success
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='PENDING')

    def save(self, *args, **kwargs):
        # Ensure recipient_new is populated based on recipient_email
        if self.recipient_email:
            recipient_profile = Profile.objects.get(user__email=self.recipient_email)
            self.recipient_id = recipient_profile.id  # Assign the ID of the recipient profile
        super().save(*args, **kwargs)


class PaymentRequest(models.Model):
    sender = models.ForeignKey(Account, related_name='sent_requests', on_delete=models.CASCADE)
    recipient_email = models.EmailField()
    recipient = models.ForeignKey(Account, related_name='received_requests', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_request = models.BooleanField(default=False)
    currency = models.CharField(max_length=3)
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('SUCCESS', 'Success'),
    ]
    # if it is normal transaction just set as Success
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='PENDING')


class Notification(models.Model):
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='notifications', on_delete=models.CASCADE, null=True)
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_notifications', on_delete=models.CASCADE, null=True)
    payment_request = models.ForeignKey(PaymentRequest, on_delete=models.CASCADE, null=True, blank=True)
    # FK to PaymentRequest
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Notification for {self.to_user.username} from {self.from_user.username}'
