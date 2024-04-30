from django.urls import path
from currency_conversion.views import conversion
from django.urls import register_converter, path


class FloatConverter:
    regex = '[+-]?([0-9]*[.])?[0-9]+'

    def to_python(self, value):
        return float(value)

    def to_url(self, value):
        return str(value)


register_converter(FloatConverter, 'float')

app_name = 'currency_conversion'
urlpatterns = [
    path('conversion/<str:base>/<str:target>/<float:amount>/', conversion, name='conversion'),
]
