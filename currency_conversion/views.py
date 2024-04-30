from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from decimal import Decimal


# Hard-coded exchange rates
EXCHANGE_RATES = {
    'USD': {
        'EUR': 0.85,
        'GBP': 0.75,
    },
    'EUR': {
        'USD': 1.18,
        'GBP': 0.88,
    },
    'GBP': {
        'USD': 1.33,
        'EUR': 1.14,
    },
}


@api_view(['GET'])
def conversion(request, base, target, amount):
    # Check if base and target currencies are in our exchange rates
    if base not in EXCHANGE_RATES or target not in EXCHANGE_RATES[base]:
        return Response({'error': 'Currency not supported.'}, status=status.HTTP_400_BAD_REQUEST)

    conversion_rate = Decimal(str(EXCHANGE_RATES[base][target]))
    converted_amount = Decimal(str(amount)) * conversion_rate

    return Response({'converted_amount': converted_amount})
