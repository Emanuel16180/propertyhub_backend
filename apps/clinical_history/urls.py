# apps/clinical_history/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Para el paciente - ver todos sus documentos
    path('my-documents/', views.MyDocumentsListView.as_view(), name='my-documents'),

    # Para el psicólogo - ver sus pacientes y subir documentos
    path('my-patients/', views.MyPastPatientsListView.as_view(), name='my-past-patients'),
    path('documents/upload/', views.DocumentUploadView.as_view(), name='document-upload'),
]