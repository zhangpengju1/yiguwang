from django.urls import path
from account import views

urlpatterns = [
    path('funds/', views.Ubalance.as_view()),
    path('receiving_address/', views.Udelivery.as_view()),
    path('register/', views.Register.as_view()),
    path('sendmail/', views.Sendmail.as_view()),
    path('verifycode/',views.Verifycode.as_view()),
    path('set-password/', views.Resetpswd.as_view()),
    path('forget-passwd/', views.Forgetpswd.as_view()),
]
