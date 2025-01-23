from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from .views import *
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'books', BookViewSet)
router.register(r'authors', AuthorViewSet)
router.register(r'borrowers', BorrowerViewSet)
router.register(r'borrowing-transaction', BorrowingTransactionViewSet)
router.register(r'reservation', ReservationViewSet)
router.register(r'reviews', ReviewViewSet)
router.register(r'reports', ReportViewSet, basename='reports')

urlpatterns = [
    path('api/', include(router.urls)),
]
