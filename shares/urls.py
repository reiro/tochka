from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<str:ticker>/', views.ticker, name='ticker'),
	path('<str:ticker>/insider/', views.insider, name='insider'),
	path('<str:ticker>/insider/<str:insider_name>/', views.insider_trades, name='insider_trades'),
    path('<str:ticker>/analytics/', views.analytics, name='analytics'),
    path('<str:ticker>/delta/', views.delta, name='delta'),
]
