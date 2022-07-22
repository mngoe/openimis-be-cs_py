from django.urls import path
from . import views


urlpatterns = [path("cheque/importfile/uploads", views.upload_cheque_file), ]
