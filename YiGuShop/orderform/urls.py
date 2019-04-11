from django.urls import path
from orderform import views

urlpatterns = [
    path('search/', views.Search.as_view()),
    path('indent/',views.Indent.as_view()),
    path('details/',views.Details.as_view()),
]
