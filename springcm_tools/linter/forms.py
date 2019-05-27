from django import forms

class UploadFileForm(forms.Form):
    file = forms.FileField(label="Select a SpringCM Template", help_text="max. 2MB")