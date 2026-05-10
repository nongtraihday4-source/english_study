import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("curriculum", "0008_add_listening_speaking_writing_content"),
    ]

    operations = [
        migrations.AddField(
            model_name="lessoncontent",
            name="learning_objectives",
            field=models.JSONField(
                blank=True,
                default=list,
                help_text='["Understand present simple", "Learn 10 vocab words"]',
            ),
        ),
    ]