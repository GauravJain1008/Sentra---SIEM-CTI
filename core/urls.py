from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('live/', views.live_logs, name='live_logs'),
    path('api/ingest/', views.ingest, name='ingest'),
    path('api/stats/', views.stats_api, name='stats_api'),
    path('api/search/', views.search_logs, name='search_logs'),
    path('api/logs/', views.fetch_logs, name='fetch_logs'),

]

