from django.urls import path
from .views import *


urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    # path('profile/<int:pk>/', UserProfileView.as_view(), name='user-profile-detail'),

]
