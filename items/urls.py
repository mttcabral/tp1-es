from django.urls import path

from .views import ClaimAcceptView, ClaimCreateView, ClaimRejectView, CommentCreateView, ItemCreateView, ItemDetailView, ItemListView

urlpatterns = [
    path('', ItemListView.as_view(), name='item_list'),
    path('new/', ItemCreateView.as_view(), name='item_create'),
    path('<int:pk>/', ItemDetailView.as_view(), name='item_detail'),
    path('<int:pk>/claims/', ClaimCreateView.as_view(), name='claim_create'),
    path('claims/<int:pk>/accept/', ClaimAcceptView.as_view(), name='claim_accept'),
    path('claims/<int:pk>/reject/', ClaimRejectView.as_view(), name='claim_reject'),
    path('<int:pk>/comments/', CommentCreateView.as_view(), name='comment_create'),
]
