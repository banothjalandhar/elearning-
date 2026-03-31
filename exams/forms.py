from django import forms

from .models import Exam, Option, Question, StudentAnswer


class ExamForm(forms.ModelForm):
    available_from = forms.DateTimeField(
        required=False,
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
    )
    available_until = forms.DateTimeField(
        required=False,
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
    )

    class Meta:
        model = Exam
        fields = ["course", "title", "category", "duration", "total_marks", "is_active", "available_from", "available_until"]
        widgets = {
            "course": forms.Select(attrs={"class": "form-select"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "duration": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "total_marks": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        available_from = cleaned_data.get("available_from")
        available_until = cleaned_data.get("available_until")
        if available_from and available_until and available_until <= available_from:
            self.add_error("available_until", "Close time must be after the start time.")
        return cleaned_data


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ["exam", "question_text", "question_type", "marks"]
        widgets = {
            "exam": forms.Select(attrs={"class": "form-select"}),
            "question_text": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            "question_type": forms.Select(attrs={"class": "form-select"}),
            "marks": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
        }


class OptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ["question", "option_text", "is_correct"]
        widgets = {
            "question": forms.Select(attrs={"class": "form-select"}),
            "option_text": forms.TextInput(attrs={"class": "form-control"}),
            "is_correct": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class ExamExcelUploadForm(forms.Form):
    exam = forms.ModelChoiceField(
        queryset=Exam.objects.select_related("course").order_by("title"),
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    file = forms.FileField(
        widget=forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".xlsx,.xls"}),
        help_text="Upload an Excel file with columns: exam, question, option1, option2, option3, option4, correct. The selected dropdown exam will be used for all imported rows.",
    )

    def clean_file(self):
        uploaded_file = self.cleaned_data["file"]
        allowed_extensions = (".xlsx", ".xls")
        if not uploaded_file.name.lower().endswith(allowed_extensions):
            raise forms.ValidationError("Please upload a valid Excel file (.xlsx or .xls).")
        return uploaded_file


class StudentAnswerForm(forms.ModelForm):
    class Meta:
        model = StudentAnswer
        fields = ["selected_option", "text_answer", "code_answer", "programming_language"]
        widgets = {
            "selected_option": forms.RadioSelect(),
            "text_answer": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            "code_answer": forms.Textarea(
                attrs={"class": "form-control font-monospace", "rows": 12, "spellcheck": "false"}
            ),
            "programming_language": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        question = kwargs.pop("question", None)
        super().__init__(*args, **kwargs)
        self.fields["selected_option"].required = False
        self.fields["text_answer"].required = False
        self.fields["code_answer"].required = False
        self.fields["programming_language"].required = False

        if question is not None:
            self.fields["selected_option"].queryset = question.options.all()
            if question.question_type != Question.QuestionType.MCQ:
                self.fields.pop("selected_option")
            if question.question_type != Question.QuestionType.TEXT:
                self.fields.pop("text_answer")
            if question.question_type != Question.QuestionType.CODE:
                self.fields.pop("code_answer")
                self.fields.pop("programming_language")
