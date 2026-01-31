from django.contrib import admin
from .models import Lead, LeadAIInsight, Task, ActivityLog

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
	list_display = ("name", "email", "status", "assigned_to", "created_at")
	list_filter = ("status", "source")
	search_fields = ("name", "email", "company")

@admin.register(LeadAIInsight)
class LeadAIInsightAdmin(admin.ModelAdmin):
	list_display = ("lead", "category", "priority_score", "created_at")
	list_filter = ("category",)

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
	list_display = ("title", "lead", "status", "assigned_to", "due_date", "created_at")
	list_filter = ("status",)

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
	list_display = ("action_type", "lead", "actor", "created_at")
	list_filter = ("action_type",)
