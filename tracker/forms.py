from django import forms
from .models import JobFolder, JobApplication, LearningEntry


class JobFolderForm(forms.ModelForm):
    class Meta:
        model = JobFolder
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "input",
                    "placeholder": "Folder name (e.g., LinkedIn, Indeed, Referrals)...",
                    "required": True,
                }
            )
        }


class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ["company_name", "job_title", "job_url", "status", "application_date", "folder", "notes"]
        widgets = {
            "company_name": forms.TextInput(
                attrs={"class": "input", "placeholder": "Organization (e.g., Deloitte, Microsoft, Google)", "required": True}
            ),
            "job_title": forms.TextInput(
                attrs={"class": "input", "placeholder": "Role (e.g., AI Engineer, Software Engineer)", "required": True}
            ),
            "job_url": forms.URLInput(
                attrs={"class": "input", "placeholder": "https://..."}
            ),
            "status": forms.Select(
                attrs={"class": "input"}
            ),
            "application_date": forms.DateInput(
                attrs={"class": "input", "type": "date"}
            ),
            "folder": forms.Select(
                attrs={"class": "input"}
            ),
            "notes": forms.Textarea(
                attrs={"class": "input", "rows": 4, "placeholder": "Interview notes, contact details, recruiter tips..."}
            ),
        }

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields["folder"].queryset = JobFolder.objects.filter(user=user)
            self.fields["folder"].empty_label = "-- Select App / Folder (Optional) --"
        if "application_date" in self.fields:
            self.fields["application_date"].required = False

    def clean_application_date(self):
        date = self.cleaned_data.get("application_date")
        if not date:
            from django.utils import timezone
            return timezone.now().date()
        return date

    def clean_status(self):
        return self.cleaned_data.get("status", "Applied")


class LearningEntryForm(forms.ModelForm):
    class Meta:
        model = LearningEntry
        fields = ["title", "date", "notes", "code_snippet", "code_language"]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "input", "placeholder": "Enter title...", "required": True}
            ),
            "date": forms.DateInput(
                attrs={"class": "input", "type": "date", "required": True}
            ),
            "notes": forms.Textarea(
                attrs={"class": "input", "placeholder": "Document your learning...", "required": True, "rows": 6}
            ),
            "code_snippet": forms.Textarea(
                attrs={"class": "input", "placeholder": "Paste your code here...", "rows": 8}
            ),
            "code_language": forms.Select(
                choices=[
                    ("", "---------"),
                    ("python", "Python"),
                    ("javascript", "JavaScript"),
                    ("java", "Java"),
                    ("csharp", "C#"),
                    ("cpp", "C++"),
                    ("c", "C"),
                    ("ruby", "Ruby"),
                    ("go", "Go"),
                    ("rust", "Rust"),
                    ("php", "PHP"),
                    ("swift", "Swift"),
                    ("kotlin", "Kotlin"),
                    ("sql", "SQL"),
                    ("html", "HTML/Markup"),
                    ("css", "CSS"),
                    ("typescript", "TypeScript"),
                    ("bash", "Bash"),
                    ("json", "JSON"),
                    ("yaml", "YAML"),
                ],
                attrs={"class": "input"},
            ),
        }
