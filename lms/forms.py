from django import forms
from .models import Quiz, QuizQuestion, QuizOption
from .models import QuizResponse

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['course', 'quiz_title', 'max_marks', 'duration']

class QuizQuestionForm(forms.ModelForm):
    class Meta:
        model = QuizQuestion
        fields = ['quiz','question_text', 'question_type', 'max_marks']
        
def __init__(self, *args, **kwargs):
        # Handle optional question parameter if needed
        self.question = kwargs.pop('question', None)  # Use pop with a default to avoid KeyError
        super().__init__(*args, **kwargs)
        if self.question is not None:
            self.fields['question_text'].initial = self.question.question_text
            self.fields['question_type'].initial = self.question.question_type
            self.fields['max_marks'].initial = self.question.max_marks        

class QuizOptionForm(forms.ModelForm):
    class Meta:
        model = QuizOption
        fields = ['option_no', 'option_text', 'is_correct','question']


class QuizResponseForm(forms.ModelForm):
    class Meta:
        model = QuizResponse
        fields = ['selected_option']  # Include fields as needed
        widgets = {
            'selected_option': forms.RadioSelect(),  # Use radio buttons for multiple-choice
        }

class QuizQuestionForm(forms.ModelForm):
    class Meta:
        model = QuizResponse
        fields = ['selected_option']  # Only include the selected option for the quiz response
     