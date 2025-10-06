# apps/tenants/urls.py

from django.urls import path
from .views import ClinicListCreateView, ClinicDetailView

app_name = 'tenants'

urlpatterns = [
    path('clinics/', ClinicListCreateView.as_view(), name='clinic-list-create'),
    path('clinics/<int:pk>/', ClinicDetailView.as_view(), name='clinic-detail'),
]