from django.contrib import admin
from .models import *
from django.contrib.auth.models import User
# Register your models here.
admin.site.register(Users)
admin.site.register(Person)
admin.site.register(GpsDevice)
admin.site.register(Vehicle)
admin.site.register(Driver)
admin.site.register(GpsData)


