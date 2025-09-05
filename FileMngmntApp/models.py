from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class CustomTable(models.Model):

    display_name = models.CharField(max_length=100)   # User-friendly name
    table_name = models.CharField(max_length=100, unique=True)  # Safe table name
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.display_name
    
class customFields(models.Model):

    table = models.ForeignKey(CustomTable, on_delete=models.CASCADE, related_name='fields')
    display_name = models.CharField(max_length=100)  # Original name
    field_name = models.CharField(max_length=100)    # Safe name
    field_type = models.CharField(max_length=50)     # SQL type
    max_length = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.display_name} ({self.field_type})"

