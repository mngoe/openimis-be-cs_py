from django.urls import path
from . import views

urlpatterns = [
    path("importfile/upload", views.upload_cheque_file, name='upload')
]