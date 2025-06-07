from django.urls import path
from .views import *


urlpatterns = [
    path('signup/',                     SignupView.as_view(),            name='signup'),
    path('login/',                      LoginView.as_view(),             name='login'),
    path('changepassword/',             ChangePasswordView.as_view(),    name='change-password'),
    path('forget/password/',            ForgetPasswordView.as_view(),    name='forget-password'),
    path('reset/password/',             ResetPasswordView.as_view(),     name='reset-password'),
    path('profile/',                    UserProfileView.as_view(),       name='user-profile'),
    path('users/',                      UserListView.as_view(),          name='user-list'),

]
