from django.urls import path

from . import views

urlpatterns = [
    path("", views.UnivercityView.as_view(), name="universiry_view"),
    path("refrence", views.ReferenceView.as_view(), name="refrence_view"),
]
