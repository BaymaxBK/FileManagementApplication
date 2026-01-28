from django.contrib import admin
from .models import customFields,CustomTable

from django.contrib import admin
from .models import CustomTable

@admin.register(CustomTable)
class CustomTableAdmin(admin.ModelAdmin):
    list_display = ("display_name", "table_name", "created_by", "created_at")
    filter_horizontal = ("visible_to_users", "visible_to_groups","users_can_edit")  # nice UI for ManyToMany

# Register your models here.
