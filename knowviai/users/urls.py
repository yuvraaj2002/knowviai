from django.urls import path
from .views import SignupView, SigninView, RefreshTokenView, UserProfileEditView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('signin/', SigninView.as_view(), name='signin'),
    path('token/refresh/', RefreshTokenView.as_view(), name='token_refresh'),
    path('profile/edit/', UserProfileEditView.as_view(), name='profile_edit'),
]
