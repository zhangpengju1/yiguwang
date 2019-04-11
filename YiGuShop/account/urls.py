from django.urls import path
from account import views

urlpatterns = [
    path('funds/', views.Ubalance.as_view()),
    path('receiving_address/', views.Udelivery.as_view()),
]
