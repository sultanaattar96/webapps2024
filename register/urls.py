from django.urls import path
from .views import home, profile, RegisterView, dashboard, register_admin, users_list

urlpatterns = [
    path('', home, name='users-home'),
    path('register/', RegisterView.as_view(), name='users-register'),
    path('profile/', profile, name='users-profile'),
    path('dashboard/', dashboard, name='users-dashboard'),
    path('register_admin/', register_admin, name='register_admin'),
    path('users_list/', users_list, name='users_list'),

]
