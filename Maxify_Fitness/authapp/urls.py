from django.urls import path
from authapp import views

urlpatterns = [
    path('',views.HomeView,name="Home"),  # Add your URL patterns here
]