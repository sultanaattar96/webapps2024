from django.urls import register_converter, path
from .views import transactions, transfer_money, \
    PaymentRequestView, NotificationView, PaymentApprovalView, PayRequestStatusView, success_view


# class FloatConverter:
#     regex = '[+-]?([0-9]*[.])?[0-9]+'
#
#     def to_python(self, value):
#         return float(value)
#
#     def to_url(self, value):
#         return str(value)
#
#
# register_converter(FloatConverter, 'float')

app_name = 'payapp'
urlpatterns = [
    path('transactions/', transactions, name='account-transactions'),
    path('transfer_money/', transfer_money, name='account-transfer_money'),
    path('request_payment/', PaymentRequestView.as_view(), name='account-request_payment'),
    path('notification/', NotificationView.as_view(), name='account-notification'),
    path('payment_approval/', PaymentApprovalView.as_view(), name='account-payment_approval'),
    path('payment_requested_status/', PayRequestStatusView.as_view(), name='account-payment_requested_status'),
    path('success/<str:action>/', success_view, name='account-success'),
    # path('conversion/<str:base>/<str:target>/<float:amount>/', conversion, name='conversion'),

]
