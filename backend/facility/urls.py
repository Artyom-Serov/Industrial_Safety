from django.urls import path

from .views import (ExaminationCreateView, ExaminationDeleteView,
                    ExaminationUpdateView, IndexView)

app_name = 'facility'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path(
        'create/',
        ExaminationCreateView.as_view(),
        name='create_examination'
    ),
    path(
        'update/<int:pk>/',
        ExaminationUpdateView.as_view(),
        name='update_examination'
    ),
    path(
        'delete/<int:pk>/',
        ExaminationDeleteView.as_view(),
        name='delete_examination'
    ),
]
