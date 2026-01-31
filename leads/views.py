
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Avg
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import LeadForm, LeadStatusForm, TaskForm
from .models import Lead, Task, ActivityLog
from .services import triage_lead_with_ai, save_ai_insight, apply_automation_rules

@login_required
def dashboard(request):
	today = timezone.now().date()
	leads_today = Lead.objects.filter(created_at__date=today).count()
	total_leads = Lead.objects.count()

	by_status = Lead.objects.values("status").annotate(c=Count("status")).order_by("status")
	high_priority = Lead.objects.filter(ai__priority_score__gte=70).count()

	context = {
		"leads_today": leads_today,
		"total_leads": total_leads,
		"high_priority": high_priority,
		"by_status": by_status,
	}
	return render(request, "leads/dashboard.html", context)

@login_required
def lead_list(request):
	qs = Lead.objects.all().order_by("-created_at")
	status = request.GET.get("status") or ""
	if status:
		qs = qs.filter(status=status)

	assigned = request.GET.get("assigned") or ""
	if assigned == "me":
		qs = qs.filter(assigned_to=request.user)

	return render(request, "leads/lead_list.html", {"leads": qs, "status": status, "assigned": assigned})

@login_required
def lead_detail(request, pk):
	lead = get_object_or_404(Lead, pk=pk)
	status_form = LeadStatusForm(instance=lead)
	task_form = TaskForm()

	if request.method == "POST":
		if "update_status" in request.POST:
			status_form = LeadStatusForm(request.POST, instance=lead)
			if status_form.is_valid():
				status_form.save()
				ActivityLog.objects.create(
					lead=lead, actor=request.user, action_type="status_updated",
					payload={"status": lead.status, "assigned_to": str(lead.assigned_to_id)}
				)
				messages.success(request, "Lead updated.")
				return redirect("lead_detail", pk=lead.pk)

		if "add_task" in request.POST:
			task_form = TaskForm(request.POST)
			if task_form.is_valid():
				task = task_form.save(commit=False)
				task.lead = lead
				task.save()
				ActivityLog.objects.create(
					lead=lead, actor=request.user, action_type="task_created", payload={"task": task.title}
				)
				messages.success(request, "Task added.")
				return redirect("lead_detail", pk=lead.pk)

		if "run_ai" in request.POST:
			result = triage_lead_with_ai(lead)
			save_ai_insight(lead, result, actor=request.user)
			apply_automation_rules(lead, actor=request.user)
			messages.success(request, "AI triage completed.")
			return redirect("lead_detail", pk=lead.pk)

	activity = lead.activity.all().order_by("-created_at")
	tasks = lead.tasks.all().order_by("-created_at")

	return render(
		request,
		"leads/lead_detail.html",
		{"lead": lead, "status_form": status_form, "task_form": task_form, "activity": activity, "tasks": tasks},
	)

@login_required
def lead_create(request):
	if request.method == "POST":
		form = LeadForm(request.POST)
		if form.is_valid():
			lead = form.save()
			ActivityLog.objects.create(
				lead=lead, actor=request.user, action_type="lead_created", payload={"email": lead.email}
			)
			messages.success(request, "Lead created.")

			# Optional: auto-run AI on create
			result = triage_lead_with_ai(lead)
			save_ai_insight(lead, result, actor=request.user)
			apply_automation_rules(lead, actor=request.user)

			return redirect("lead_detail", pk=lead.pk)
	else:
		form = LeadForm()
	return render(request, "leads/lead_create.html", {"form": form})
