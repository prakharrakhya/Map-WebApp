
from django.contrib import admin
from core.views import Home
from django.urls import path

urlpatterns = [
    path('' , Home , name = 'home'),
    path('admin/', admin.site.urls),
    
]
