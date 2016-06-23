from django import forms

class TaskForm(forms.Form):
    task_name = forms.CharField(label='Task Name', max_length=100)
    remote = forms.BooleanField(label='Run task remotely?', required=False)

class ArgumentForm(forms.Form):
    argument = forms.CharField(label='Argument', max_length=100)

class EnvironmentForm(forms.Form):
    variable_name = forms.CharField(label='Name', max_length=100)
    variable_value = forms.CharField(label='Value', max_length=100)
