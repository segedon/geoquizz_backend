from django.urls import path
from .views import (user_registration, user_login, user_info,
                    user_logout, change_password, liked_category)


urlpatterns = [
    path('registration/', user_registration, name='user_registration'),
    path('login/', user_login, name='user_login'),
    path('logout/', user_logout, name='user_logout'),
    path('info/', user_info, name='user_info'),
    path('change_password/', change_password, name='change_password'),
    path('liked_category/', liked_category, name='liked_category'),
]

