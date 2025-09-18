from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home'),
    path('predict/', views.predict_image, name='predict'),
    path('history/', views.prediction_history, name='history'),
]
