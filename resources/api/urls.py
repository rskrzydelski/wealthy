from django.urls import re_path
from . import views


app_name = 'resources'
urlpatterns = [
    re_path(r'metals$', views.MetalLstCreateAPIView.as_view(), name='res-create-lst'),
    re_path(r'metals/(?P<pk>\d+)$', views.MetalDetailDelUpdateAPIView.as_view(), name='res-detail'),
    re_path(r'currency$', views.CurrencyLstCreateAPIView.as_view(), name='curr-create-lst'),
    re_path(r'currency/(?P<pk>\d+)$', views.CurrencyDetailAPIView.as_view(), name='curr-detail'),
    re_path(r'cash$', views.CashLstCreateAPIView.as_view(), name='cash-create-lst'),
]
