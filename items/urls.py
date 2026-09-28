from django.urls import path

from .views import ClaimCreateView, ItemCreateView, ItemDetailView, ItemListView

urlpatterns = [
    path('', ItemListView.as_view(), name='item_list'),
    path('new/', ItemCreateView.as_view(), name='item_create'),
    path('<int:pk>/', ItemDetailView.as_view(), name='item_detail'),
    path('<int:pk>/claims/', ClaimCreateView.as_view(), name='claim_create'),
]
