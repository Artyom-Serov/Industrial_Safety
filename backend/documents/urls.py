from django.urls import path

from .views import document_generate_view

app_name = 'documents'

urlpatterns = [
    path('generate/<int:examination_id>/',
         document_generate_view,
         name='document_generate')
]
