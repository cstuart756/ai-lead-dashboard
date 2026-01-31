import os
import json
from django.conf import settings
from .models import LeadAIInsight, ActivityLog

def _safe_int(x, default=0):
    try:
        return int(x)
    except Exception:
        return default

def triage_lead_with_ai(lead):
    """
    Returns dict:
      summary: str
      category: str
      priority_score: int
      extracted_requirements: dict
      model_used: str
    """
    api_key = getattr(settings, "OPENAI_API_KEY", "") or os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        # No key set: fall back to deterministic "no-ai" behavior for dev/demo
        result = {
            "summary": "AI disabled: no OPENAI_API_KEY set.",
            "category": "Unknown",
            "priority_score": 10,
            "extracted_requirements": {"note": "Set OPENAI_API_KEY to enable AI triage."},
            "model_used": "none",
        }
        return result

    # Lazy import so app runs without OpenAI configured
    from openai import OpenAI
    client = OpenAI(api_key=api_key)

    system = (
        "You are an operations assistant. "
        "Given a sales lead, return ONLY valid JSON with keys: "
        "summary (string), category (string), priority_score (0-100 int), extracted_requirements (object). "
        "No markdown, no extra text."
    )

    user = {
        "name": lead.name,
        "email": lead.email,
        "company": lead.company,
        "message": lead.message,
        "source": lead.source,
        "budget_range": lead.budget_range,
        "urgency": lead.urgency,
    }

    resp = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(user)},
        ],
    )

    text = resp.output_text.strip()
    try:
        data = json.loads(text)
    except Exception:
        # If model output isn't valid JSON, store fallback
        data = {
            "summary": text[:500],
            "category": "Unparsed",
            "priority_score": 20,
            "extracted_requirements": {"raw": text[:2000]},
        }

    return {
        "summary": str(data.get("summary", ""))[:2000],
        "category": str(data.get("category", ""))[:100],
        "priority_score": max(0, min(100, _safe_int(data.get("priority_score", 0), 0))),
        "extracted_requirements": data.get("extracted_requirements", {}) if isinstance(data.get("extracted_requirements", {}), dict) else {},
        "model_used": "gpt-4.1-mini",
    }

def save_ai_insight(lead, result, actor=None):
    insight, _ = LeadAIInsight.objects.update_or_create(
        lead=lead,
        defaults={
            "summary": result["summary"],
            "category": result["category"],
            "priority_score": result["priority_score"],
            "extracted_requirements": result["extracted_requirements"],
            "model_used": result["model_used"],
        },
    )
    ActivityLog.objects.create(
        lead=lead,
        actor=actor,
        action_type="ai_triage_completed",
        payload={"category": insight.category, "priority_score": insight.priority_score},
    )
    return insight

def apply_automation_rules(lead, actor=None):
    """
    Simple rules:
    - if AI score > 70 -> mark QUALIFIED
    - auto-assign if unassigned and staff exists
    """
    score = getattr(lead.ai, "priority_score", 0) if hasattr(lead, "ai") else 0

    changed = False
    if score >= 70 and lead.status == lead.Status.NEW:
        lead.status = lead.Status.QUALIFIED
        changed = True

    if changed:
        lead.save(update_fields=["status"])
        ActivityLog.objects.create(
            lead=lead, actor=actor, action_type="status_auto_updated", payload={"status": lead.status}
        )
