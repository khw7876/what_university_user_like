from django.urls import path

from . import views

urlpatterns = [
    path("", views.UnivercityView.as_view(), name="universiry_view"),
]
