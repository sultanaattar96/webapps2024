from django import forms
from rest_framework import serializers
from .models import Notification, Transaction, PaymentRequest


class PaymentRequestForm(forms.ModelForm):
    class Meta:
        model = PaymentRequest
        fields = ['recipient_email', 'amount', 'currency']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'to_user', 'from_user', 'transaction', 'message', 'is_read']
        # Optionally, you can use '__all__' to include all fields
        # fields = '__all__'


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['recipient_email', 'amount', 'currency']


class PaymentApprovalForm(forms.Form):
    payment_request_id = forms.CharField(label='Payment Request ID', max_length=100)
    action = forms.ChoiceField(label='Action', choices=[('approve', 'Approve'), ('reject', 'Reject')])

    def clean(self):
        cleaned_data = super().clean()
        payment_request_id = cleaned_data.get('payment_request_id')
        action = cleaned_data.get('action')

        if not payment_request_id or action not in ['approve', 'reject']:
            raise forms.ValidationError(
                'Invalid request data. Please provide a valid payment request ID and select an action.')

        return cleaned_data
