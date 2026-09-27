from django.urls import path

from .views import CommentCreateView, ItemCreateView, ItemDetailView

urlpatterns = [
    path('new/', ItemCreateView.as_view(), name='item_create'),
    path('<int:pk>/', ItemDetailView.as_view(), name='item_detail'),
    path('<int:pk>/comments/', CommentCreateView.as_view(), name='comment_create'),
]
