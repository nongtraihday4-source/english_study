"""
Data migration: port existing LessonContent flat grammar fields and skill exercises
into the new grammar_sections / skill_sections JSONFields.
"""
from django.db import migrations


_SKILL_TYPES = {"dictation", "shadowing", "guided-writing"}


def port_to_sections(apps, schema_editor):
    LessonContent = apps.get_model("curriculum", "LessonContent")

    for lc in LessonContent.objects.all():
        # ── grammar_sections ──────────────────────────────────────────
        if not lc.grammar_sections and lc.grammar_title:
            knowledge_exs = [
                e for e in (lc.exercises or [])
                if e.get("type") not in _SKILL_TYPES
            ]
            lc.grammar_sections = [{
                "title": lc.grammar_title,
                "grammar_topic_id": lc.grammar_topic_id,
                "note": lc.grammar_note,
                "examples": lc.grammar_examples or [],
                "exercises": knowledge_exs,
            }]

        # ── skill_sections ────────────────────────────────────────────
        if not lc.skill_sections:
            skill_map = {"dictation": [], "shadowing": [], "guided_writing": []}
            for ex in (lc.exercises or []):
                t = ex.get("type")
                if t == "dictation":
                    skill_map["dictation"].append(ex)
                elif t == "shadowing":
                    skill_map["shadowing"].append(ex)
                elif t == "guided-writing":
                    skill_map["guided_writing"].append(ex)
            if any(skill_map.values()):
                lc.skill_sections = skill_map

        lc.save(update_fields=["grammar_sections", "skill_sections"])


def reverse_port(apps, schema_editor):
    # No-op: old fields still intact, just clear new ones
    LessonContent = apps.get_model("curriculum", "LessonContent")
    LessonContent.objects.all().update(grammar_sections=[], skill_sections={})


class Migration(migrations.Migration):

    dependencies = [
        ("curriculum", "0006_add_grammar_skill_sections"),
    ]

    operations = [
        migrations.RunPython(port_to_sections, reverse_port),
    ]
