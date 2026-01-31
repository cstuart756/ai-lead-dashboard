
from django.conf import settings
from django.db import models
from django.utils import timezone
import uuid

class Lead(models.Model):
	class Status(models.TextChoices):
		NEW = "NEW", "New"
		QUALIFIED = "QUALIFIED", "Qualified"
		CONTACTED = "CONTACTED", "Contacted"
		BOOKED = "BOOKED", "Booked"
		CLOSED = "CLOSED", "Closed"

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	name = models.CharField(max_length=120)
	email = models.EmailField()
	company = models.CharField(max_length=200, blank=True)
	message = models.TextField()
	source = models.CharField(max_length=50, blank=True)
	budget_range = models.CharField(max_length=50, blank=True)
	urgency = models.CharField(max_length=50, blank=True)

	status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
	assigned_to = models.ForeignKey(
		settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="assigned_leads"
	)

	created_at = models.DateTimeField(default=timezone.now)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"{self.name} ({self.email})"


class LeadAIInsight(models.Model):
	lead = models.OneToOneField(Lead, on_delete=models.CASCADE, related_name="ai")
	summary = models.TextField(blank=True)
	category = models.CharField(max_length=100, blank=True)
	priority_score = models.IntegerField(default=0)
	extracted_requirements = models.JSONField(default=dict, blank=True)
	model_used = models.CharField(max_length=100, blank=True)
	created_at = models.DateTimeField(default=timezone.now)

	def __str__(self):
		return f"AI Insight for {self.lead_id}"


class Task(models.Model):
	class Status(models.TextChoices):
		OPEN = "OPEN", "Open"
		DONE = "DONE", "Done"

	lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="tasks")
	title = models.CharField(max_length=200)
	due_date = models.DateField(null=True, blank=True)
	status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)
	assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
	created_at = models.DateTimeField(default=timezone.now)

	def __str__(self):
		return self.title


class ActivityLog(models.Model):
	lead = models.ForeignKey(Lead, null=True, blank=True, on_delete=models.SET_NULL, related_name="activity")
	actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
	action_type = models.CharField(max_length=100)
	payload = models.JSONField(default=dict, blank=True)
	created_at = models.DateTimeField(default=timezone.now)

	def __str__(self):
		return f"{self.action_type} @ {self.created_at:%Y-%m-%d %H:%M}"
