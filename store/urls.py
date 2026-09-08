from django.urls import path
from . import views

urlpatterns = [
    path("", views.store_index, name="store_index"),
    path("branch/<int:branch_id>/", views.branch_detail, name="branch_detail"),
]