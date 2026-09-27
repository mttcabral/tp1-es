from django.urls import path
from .views import ItemCreateView, ItemDetailView, ItemListView

urlpatterns = [
    path('', ItemListView.as_view(), name='item_list'),
    path('new/', ItemCreateView.as_view(), name='item_create'),
    path('<int:pk>/', ItemDetailView.as_view(), name='item_detail'),
]
