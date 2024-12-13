from django.urls import path
from .views import IndexView, create_examination, update_examination, delete_examination

app_name = 'facility'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('create/', create_examination, name='create_examination'),
    path('update/<int:pk>/', update_examination, name='update_examination'),
    path('delete/<int:pk>/', delete_examination, name='delete_examination'),
]
