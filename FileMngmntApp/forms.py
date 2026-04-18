from django import forms
from .models import CustomTable
from django.contrib.auth.models import User, Group

class CustomTableForm(forms.ModelForm):

    visible_to_users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.SelectMultiple(attrs={"class": "form-select"}),
        required=False
    )

    visible_to_groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=forms.SelectMultiple(attrs={"class": "form-select"}),
        required=False
    )

    users_can_edit = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.SelectMultiple(attrs={"class": "form-select"}),
        required=False
    )

    class Meta:
        model = CustomTable
        fields = ["display_name", "visible_to_users", "visible_to_groups", "users_can_edit"]
        widgets = {
            "display_name": forms.TextInput(attrs={
                "class": "form-control w-100",
                "placeholder": "Enter Project Name"
            })
        }