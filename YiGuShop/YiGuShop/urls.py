"""YiGuShop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include,re_path
from django.conf.urls import url
from search.views import YiGuView
from django.views.static import serve
from .settings import MEDIA_ROOT
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/account', include('account.urls')),
    path('api/v1/cart', include('cart.urls')),
    path('api/v1/orderform', include('orderform.urls')),
    path('api/v1/pay', include('pay.urls')),
    path('api/v1/search',YiGuView(),name='haystack_search'),
    path('api/v1/shop', include('shop.urls')),
    re_path(r'^api/v1/media/(?P<path>.*)$', serve, {"document_root":MEDIA_ROOT})
