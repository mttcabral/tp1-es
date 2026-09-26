from django.urls import path

from .views import ItemCreateView, ItemDetailView

urlpatterns = [
    path('new/', ItemCreateView.as_view(), name='item_create'),
    path('<int:pk>/', ItemDetailView.as_view(), name='item_detail'),
]
