from django.contrib import admin
from database.models import Commodity,Category,CommodityImage,Specification
# Register your models here.
admin.site.register([Commodity,Category,CommodityImage,Specification])