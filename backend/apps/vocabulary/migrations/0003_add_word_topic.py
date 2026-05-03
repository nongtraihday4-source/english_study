from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("vocabulary", "0002_add_studysession_deck_choice"),
    ]

    operations = [
        migrations.AddField(
            model_name="word",
            name="topic",
            field=models.CharField(
                blank=True,
                db_index=True,
                help_text="Vocabulary topic this word belongs to, e.g. 'Health - Symptoms & Illnesses'",
                max_length=200,
                null=True,
            ),
        ),
    ]
