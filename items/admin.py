from django.contrib import admin

from .models import Item


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'kind', 'category', 'location', 'status', 'author', 'created_at')
    list_filter = ('kind', 'status', 'category', 'location')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'
