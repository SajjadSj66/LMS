from django.urls import path, include
from rest_framework import routers
from .views import *

routers = routers.DefaultRouter()
routers.register(r'users', UserViewSet)
routers.register(r'borrowers', BorrowerViewSet)

urlpatterns = [
    path('', include(routers.urls)),
]
