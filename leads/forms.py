from django import forms
from .models import Lead, Task

class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ["name", "email", "company", "message", "source", "budget_range", "urgency"]

class LeadStatusForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ["status", "assigned_to"]

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "due_date", "status", "assigned_to"]
