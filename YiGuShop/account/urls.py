from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.Register.as_view()),
    path('sendmail/', views.Sendmail.as_view()),
    path('verifycode/',views.Verifycode.as_view()),
    path('set-password/', views.Resetpswd.as_view()),
    path('forget-passwd/', views.Forgetpswd.as_view()),
]
