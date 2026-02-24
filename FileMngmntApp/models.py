from django.db import models
from django.contrib.auth.models import User,Group

# Create your models here.
class CustomTable(models.Model):

    display_name = models.CharField(max_length=100)   # User-friendly name
    table_name = models.CharField(max_length=100, unique=True)  # Safe table name
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    visible_to_users  = models.ManyToManyField(User, blank=True, related_name="allowed_tables")
    visible_to_groups = models.ManyToManyField(Group, blank=True, related_name="group_tables")

    users_can_edit = models.ManyToManyField(User, blank=True, related_name="can_edit_tables")

    def __str__(self):
        return self.display_name
    
    def can_user_edit(self, user):
        return (
            user.is_authenticated and
            self.users_can_edit.filter(id=user.id).exists()
        )
    
class customFields(models.Model):

    table = models.ForeignKey(CustomTable, on_delete=models.CASCADE, related_name='fields')
    display_name = models.CharField(max_length=100)  # Original name
    field_name = models.CharField(max_length=100)    # Safe name
    field_type = models.CharField(max_length=50)     # SQL type
    
    field_kind = models.CharField(                  # Logical type
        max_length=20,
        choices=[
            ("text", "Text"),
            ("number", "Number"),
            ("date", "Date"),
            ("boolean", "Boolean"),
        ],
        default="text"
    )

    max_length = models.PositiveIntegerField(null=True, blank=True)

    is_primary_key = models.BooleanField(default=False)  # part of PK (single/composite)
    is_not_null    = models.BooleanField(default=False)  # adds NOT NULL
    is_unique      = models.BooleanField(default=False)  # adds UNIQUE
    
    default_value  = models.CharField(
        max_length=255, null=True, blank=True,
        help_text="Literal default value for SQL DEFAULT"
    )
 
    check_constraint = models.CharField(
        max_length=255, null=True, blank=True,
        help_text="Raw SQL for CHECK, e.g. 'age > 0'"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,null=True,
        blank=True
        )
    
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("table", "field_name")
        ordering = ["id"]

    def __str__(self):
        return f"{self.display_name} ({self.field_type})"


class TableSchemaChange(models.Model):
    table = models.ForeignKey(
        CustomTable,
        on_delete=models.CASCADE,
        related_name="schema_changes"
    )

    executed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )

    action = models.CharField(
        max_length=50,
        choices=[
            ("rename", "Rename Column"),
            ("constraint", "Alter Constraint"),
            ("add_column", "Add Column"),
            ("drop_column", "Drop Column"),
        ]
    )

    sql_executed = models.TextField()
    success = models.BooleanField(default=True)
    error_message = models.TextField(null=True, blank=True)

    executed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.table.table_name} | {self.action} | {self.executed_at}"


class CompositeUniqueConstraint(models.Model):
    table = models.ForeignKey(
        CustomTable,
        on_delete=models.CASCADE,
        related_name="composite_uniques"
    )

    fields = models.ManyToManyField(
        customFields,
        related_name="unique_groups"
    )

    def __str__(self):
        cols = ", ".join(f.field_name for f in self.fields.all())
        return f"UNIQUE ({cols})"

class CustomTaskTable(models.Model):
    
    status_choices = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
    ]

    BaseTable = models.ForeignKey(CustomTable, on_delete=models.CASCADE, related_name='baseTable',null=True,
    blank=True)
    TaskNameDisplay=models.CharField(max_length=100)
    TaskName=models.CharField(max_length=100)
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE,related_name="assignedBy")
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_to=models.ForeignKey(User,on_delete=models.CASCADE,related_name="assignedTo",null=True,
    blank=True)
    status=models.CharField(max_length=20,choices=status_choices,default="Pending")


class CustomTaskFields(models.Model):
    
    TaskTable = models.ForeignKey(CustomTaskTable, on_delete=models.CASCADE, related_name='TaskFields')
    display_name = models.CharField(max_length=100)
    field_name = models.CharField(max_length=100)    # Safe name
    field_type = models.CharField(max_length=50)     # SQL type


class AssignedTaskRows(models.Model):
    
    task = models.ForeignKey(CustomTaskTable, on_delete=models.CASCADE, related_name='TaskRows')
    assigned_from=models.ForeignKey(CustomTable,on_delete=models.CASCADE, related_name='assigned_from')
    assigned_row_id=models.IntegerField()


class Dashboard(models.Model):
    name = models.CharField(max_length=100)
    table = models.ForeignKey(CustomTable, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class DashboardGroupColumn(models.Model):
    
    dashboard = models.ForeignKey(
        Dashboard,
        on_delete=models.CASCADE,
        related_name="group_columns"
    )
    
    field = models.ForeignKey(customFields, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ["order"]