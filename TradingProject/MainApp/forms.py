# MainApp/forms.py
from django import forms
from django.core.validators import FileExtensionValidator


class UploadFileForm(forms.Form):
    file = forms.FileField(label='Select a file: ', allow_empty_file=False, required=True, validators=[FileExtensionValidator(allowed_extensions=['csv'])])
    timeframe = forms.IntegerField(label='TimeFrame: ',)
