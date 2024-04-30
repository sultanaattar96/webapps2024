from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction

from register.models import CustomUser as User
# from django.contrib.auth.models import CustomUser  as User
from django.utils.decorators import method_decorator

from timestampservice.timestampclient import TimestampClient
from .models import Transaction, Account, Notification, PaymentRequest
from .forms import TransactionForm, PaymentRequestForm, PaymentApprovalForm
from rest_framework.views import APIView
import requests
from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseBadRequest, JsonResponse

from django.conf import settings


def get_timestamp():
    timestamp_client = TimestampClient()
    timestamp = timestamp_client.get_current_timestamp()
    if timestamp:
        return timestamp
    else:
        return JsonResponse({'error': 'Unable to fetch timestamp'}, status=500)

@login_required
def transactions(request):
    errors = []
    try:
        # Check if the user is an admin
        if request.user.is_superuser:
            # If the user is an admin, retrieve all transactions
            transactions = Transaction.objects.all().order_by('-timestamp')
        else:
            user_acc = Account.objects.get(user=request.user)
            # If the user is not an admin, retrieve only their transactions
            transactions = Transaction.objects.filter(sender=user_acc) | Transaction.objects.filter(recipient=user_acc)
            transactions = transactions.order_by('-timestamp')

    except ObjectDoesNotExist:
        errors.append("User account does not exist.")
    except Exception as e:
        errors.append(str(e))

    return render(request, 'account/transactions.html', {'transactions': transactions, 'errors': errors})


@login_required
@transaction.atomic
def transfer_money(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            recipient_email = form.cleaned_data['recipient_email']
            currency = form.cleaned_data['currency']
            amount = form.cleaned_data['amount']
            try:
                with transaction.atomic():
                    # Retrieve recipient profile based on email address
                    recipient_user = User.objects.get(email=recipient_email)
                    recipient_acc = Account.objects.get(user=recipient_user)
                    user_acc = Account.objects.get(user=request.user)

                    if recipient_user.is_superuser:
                        form.add_error(None,
                                       "Sorry, Can not transfer money to admins account!")
                        return render(request, 'account/transfer_money.html', {'form': form})

                    if currency != user_acc.currency and currency != recipient_acc.currency:
                        form.add_error(None,
                                       "Selected currency must be the same as either sender's or receiver's currency.")
                    else:
                        # Check if the sender has enough balance and perform currency conversion if necessary
                        # come this logic later
                        # If the sender's currency is different from the selected currency
                        if user_acc.currency != currency:
                            # Convert the selected amount back to the sender's currency
                            response = requests.get(
                                f'{settings.BASE_URL}/currency_conversion/conversion/{currency}/{user_acc.currency}/{amount}')
                            if response.status_code == 200:
                                sender_amount = Decimal(str(response.json()['converted_amount']))
                            else:
                                print(f"Request failed with status code {response.status_code}")
                                return
                        else:
                            sender_amount = Decimal(str(amount))

                        # Check if the user has enough balance
                        if user_acc.balance >= sender_amount:
                            # If the recipient's currency is the same as the selected currency
                            if recipient_acc.currency == currency:
                                recipient_amount = Decimal(str(amount))
                            # If the recipient's currency is different from the selected currency
                            else:
                                # Convert the amount to the recipient's currency
                                response = requests.get(
                                    f'{settings.BASE_URL}/currency_conversion/conversion/{currency}/{recipient_acc.currency}/{amount}')
                                if response.status_code == 200:
                                    recipient_amount = Decimal(str(response.json()['converted_amount']))
                                else:
                                    print(f"Request failed with status code {response.status_code}")
                                    return

                            # Deduct the original amount in the sender's currency
                            user_acc.balance -= sender_amount
                            # Add the converted amount in the recipient's currency
                            recipient_acc.balance += recipient_amount
                            # Add the converted amount in the recipient's currency
                            user_acc.save()
                            recipient_acc.save()

                            # Log the transaction
                            Transaction.objects.create(
                                sender=user_acc,
                                recipient=recipient_acc,
                                amount=amount,  # Save the numeric value
                                currency=currency,  # Save the currency code
                                status='SUCCESS',
                                timestamp=get_timestamp(),
                            )
                            # Create a notification for the recipient
                            Notification.objects.create(
                                to_user=recipient_user,
                                from_user=request.user,
                                is_read=False,
                                message=f'You have received {sender_amount} {user_acc.currency}/ {recipient_amount} {recipient_acc.currency} from {request.user.username}'
                            )
                            return success_view(request, 'transfer')
                        else:
                            form.add_error(None, 'Insufficient balance.')
            except User.DoesNotExist:
                form.add_error('recipient_email', 'Recipient not found.')
            except Account.DoesNotExist:
                form.add_error('recipient_email', 'Recipient account not found.')
        return render(request, 'account/transfer_money.html', {'form': form})
    else:
        form = TransactionForm()
    return render(request, 'account/transfer_money.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class PaymentRequestView(APIView):
    def post(self, request, *args, **kwargs):
        form = PaymentRequestForm(request.POST)
        try:
            recipient_email = request.data.get('recipient_email')
            amount = request.data.get('amount')
            currency = request.data.get('currency')  # Currency in which the sender is sending the amount

            try:
                recipient_user = User.objects.get(email=recipient_email)

                if recipient_user.is_superuser:
                    form.add_error(None,
                                   "Sorry, Can not transfer money to admins account!")
                    return render(request, 'account/request_payment.html', {'form': form})

                recipient_acc = Account.objects.get(user=recipient_user)
                user_acc = Account.objects.get(user=request.user)
            except User.DoesNotExist:
                form.add_error(None, "Recipient not found.")
                return render(request, 'account/request_payment.html', {'form': form})

            with transaction.atomic():
                if currency != user_acc.currency and currency != recipient_acc.currency:
                    form.add_error(None,
                                   "Selected currency must be the same as either sender's or receiver's currency.")
                    return render(request, 'account/request_payment.html', {'form': form})
                else:
                    payment_request = PaymentRequest.objects.create(
                        # if approved this will be payer
                        sender=recipient_acc,
                        recipient_email=recipient_email,
                        # This will be receiver
                        recipient=user_acc,
                        amount=amount,
                        currency=currency,
                        is_request=True,
                        status='Pending'
                    )

                    # Create a notification for the recipient
                    Notification.objects.create(
                        to_user=recipient_user,
                        from_user=request.user,
                        payment_request=payment_request,
                        message=f'Payment request of {amount} {currency} from {request.user.username}'
                    )
                    return success_view(request, 'payment_request')
        except Exception as e:
            form.add_error(None, e)
            return render(request, 'account/request_payment.html', {'form': form})

    def get(self, request, *args, **kwargs):
        form = PaymentRequestForm()
        return render(request, 'account/request_payment.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class NotificationView(APIView):

    def get(self, request, *args, **kwargs):
        errors = []
        try:
            # Fetch notifications for the logged-in user that are unread
            notifications = Notification.objects.filter(to_user=request.user).order_by('-timestamp')

            # Fetch related payment requests for each notification
            for notification in notifications:
                # Assuming there's a foreign key in PaymentRequest pointing to Notification
                payment_request = PaymentRequest.objects.filter(notification=notification).first()
                if payment_request:
                    notification.payment_status = payment_request.status
                    # notification.payment_details = payment_request.details
                else:
                    notification.payment_status = 'No Request'
                    notification.payment_details = {}

        except ObjectDoesNotExist:
            errors.append("User account does not exist.")
        except Exception as e:
            errors.append(str(e))
        return render(request, 'account/notification.html', {'notifications': notifications, 'errors': errors})


@method_decorator(login_required, name='dispatch')
class PayRequestStatusView(APIView):
    def get(self, request, *args, **kwargs):
        errors = []
        try:
            # Check if the user is an admin
            if request.user.is_superuser:
                # If the user is an admin, retrieve all notifications
                notifications = Notification.objects.all().order_by('-timestamp')
            else:
                # If the user is not an admin, retrieve only their notifications
                notifications = Notification.objects.filter(from_user=request.user).order_by('-timestamp')

            # Fetch related payment requests for each notification
            for notification in notifications:
                # Assuming there's a foreign key in PaymentRequest pointing to Notification
                payment_request = PaymentRequest.objects.filter(notification=notification).first()
                if payment_request:
                    notification.payment_status = payment_request.status
                    # notification.payment_details = payment_request.details
                else:
                    notification.payment_status = 'No Request'
                    notification.payment_details = {}

        except ObjectDoesNotExist:
            errors.append("User account does not exist.")
        except Exception as e:
            errors.append(str(e))
        return render(request, 'account/payment_requested_status.html',
                      {'notifications': notifications, 'errors': errors})


@method_decorator(login_required, name='dispatch')
class PaymentApprovalView(APIView):
    def post(self, request, *args, **kwargs):
        form = PaymentApprovalForm(request.POST)
        try:
            payment_request_id = request.data.get('payment_request_id')
            action = request.data.get('action')

            if not payment_request_id or action not in ['approve', 'reject']:
                form.add_error(None, "Invalid request data, please select approve or reject")
                return render(request, 'account/payment_approval.html', {'form': form})

            try:
                payment_request = PaymentRequest.objects.get(id=payment_request_id)
            except PaymentRequest.DoesNotExist:
                form.add_error(None, "Payment request not found")
                return render(request, 'account/payment_approval.html', {'form': form})

            if action == 'approve':
                with transaction.atomic():
                    sender_acc = payment_request.sender
                    recipient_acc = payment_request.recipient

                    # recipient_user = User.objects.get(email=payment_request.recipient)
                    # sender_user = User.objects.get(email=payment_request.sender)
                    # recipient_acc = Account.objects.get(user=recipient_user)
                    # sender_acc = Account.objects.get(user=sender_user)

                    # print('Sultana ---> ', payment_request.sender)
                    # sender_acc = Account.objects.get(user=payment_request.sender_id)
                    # recipient_acc = Account.objects.get(user=payment_request.recipient_id)
                    user_amount = payment_request.amount
                    if sender_acc.currency != payment_request.currency:
                        # Convert the selected amount back to the sender's currency
                        response = requests.get(
                            f'{settings.BASE_URL}/currency_conversion/conversion/{payment_request.currency}/{sender_acc.currency}/{user_amount}')
                        if response.status_code == 200:
                            sender_amount = Decimal(str(response.json()['converted_amount']))
                        else:
                            print(f"Request failed with status code {response.status_code}")
                            return
                    else:
                        sender_amount = Decimal(str(user_amount))

                        # Check if the user has enough balance
                    if sender_acc.balance >= sender_amount:
                        # If the recipient's currency is the same as the selected currency
                        if recipient_acc.currency == payment_request.currency:
                            recipient_amount = Decimal(str(user_amount))
                        # If the recipient's currency is different from the selected currency
                        else:
                            # Convert the amount to the recipient's currency
                            response = requests.get(
                                f'{settings.BASE_URL}/currency_conversion/conversion/{payment_request.currency}/{recipient_acc.currency}/{user_amount}')
                            if response.status_code == 200:
                                recipient_amount = Decimal(str(response.json()['converted_amount']))
                            else:
                                print(f"Request failed with status code {response.status_code}")
                                return

                        sender_acc.balance -= sender_amount
                        recipient_acc.balance += recipient_amount
                        sender_acc.save()
                        recipient_acc.save()

                        payment_request.status = 'Approved'
                        payment_request.save()

                        # Create a transaction for the completed payment
                        Transaction.objects.create(
                            sender=sender_acc,
                            recipient=recipient_acc,
                            amount=user_amount,
                            currency=payment_request.currency,
                            status='SUCCESS',
                            timestamp=get_timestamp(),
                        )

                        # Notification.objects.create(
                        #     to_user=sender_acc,
                        #     from_user=recipient_acc,
                        #     is_read=False,
                        #     message=f'Payment request has been approved {payment_request.amount} {payment_request.currency} from {request.user.username}'
                        # )

                        # Create a new notification for the recipient
                        # Notification.objects.create(
                        #     from_user=request.user,
                        #     to_user=payment_request.sender.user,
                        #     message=f'You have received a payment of {payment_request.amount} from {request.user.username}.'
                        # )

                        # Update the notification as read
                        notification = Notification.objects.get(payment_request=payment_request)
                        notification.is_read = True
                        notification.save()
                        return success_view(request, 'payment_approved')
            elif action == 'reject':
                with transaction.atomic():
                    # Mark the payment request as rejected
                    payment_request.status = 'Rejected'
                    payment_request.save()

                    # Update the notification as read
                    notification = Notification.objects.get(payment_request=payment_request)
                    notification.is_read = True
                    notification.save()
                return success_view(request, 'payment_rejected')
        except Exception as e:
            form.add_error(None, e)
            return render(request, 'account/payment_approval.html', {'form': form})

    def get(self, request, *args, **kwargs):
        form = PaymentApprovalForm()
        try:
            payment_request_id = request.GET.get('payment_request_id')
            payment_request = get_object_or_404(PaymentRequest, id=payment_request_id)
            notification = get_object_or_404(Notification, payment_request_id=payment_request_id)
            if notification:
                payment_request.message = notification.message
                # notification.payment_details = payment_request.details
            else:
                payment_request.message = 'No Message'
            return render(request, 'account/payment_approval.html', {'payment_request': payment_request})
        except Exception as e:
            form.add_error(None, e)
            return render(request, 'account/payment_approval.html', {'form': form})


def success_view(request, action):
    if action == 'transfer':
        page_title = 'Transfer Money'
        success_message = 'Transfer Successful!'
        success_details = 'Your transfer has been processed successfully.'
    elif action == 'payment_request':
        page_title = 'Payment Request'
        success_message = 'Payment Requested Successfully!'
        success_details = 'Your payment request has been sent successfully.'
    elif action == 'payment_approved':
        page_title = 'Payment Approved'
        success_message = 'Payment Approved!'
        success_details = 'Your payment request has been approved successfully.'
    elif action == 'payment_rejected':
        page_title = 'Payment Rejected'
        success_message = 'Payment Rejected!'
        success_details = 'Your payment request has been Rejected successfully.'
    else:
        # Handle unexpected action
        page_title = 'Error'
        success_message = 'Error'
        success_details = 'An unexpected error occurred.'

    context = {
        'page_title': page_title,
        'success_message': success_message,
        'success_details': success_details,
    }
    return render(request, 'account/success.html', context)
