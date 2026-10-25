from django.db import migrations, models


def move_interviewing_to_interview(apps, schema_editor):
    JobApplication = apps.get_model("tracker", "JobApplication")
    JobApplication.objects.using(schema_editor.connection.alias).filter(
        status="Interviewing"
    ).update(status="Interview")


class Migration(migrations.Migration):

    dependencies = [
        ("tracker", "0002_jobfolder_learningentry_and_more"),
    ]

    operations = [
        migrations.RunPython(move_interviewing_to_interview, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="jobapplication",
            name="status",
            field=models.CharField(
                choices=[
                    ("Applied", "Applied"),
                    ("Interview", "Interview"),
                    ("Und Con", "Und Con"),
                    ("Offer", "Offer"),
                    ("Rejected", "Rejected"),
                    ("Interested", "Interested"),
                ],
                default="Applied",
                max_length=30,
            ),
        ),
    ]
