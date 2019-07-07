from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Layout, Div, Field

class UploadFileForm(forms.Form):
    file = forms.FileField(label="Upload SpringCM Template (.docx)")
    terms = forms.BooleanField(label="I acknowledge this was built for fun so there are NO WARRANTIES. I'm using this at my own risk.")

    def __init__(self, *args, **kwargs):
        super(UploadFileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.form_action = 'linter:index'
        self.helper.layout = Layout(
            Field('file'),
            HTML('<hr />'),
            Field('terms', template="linter/custom_checkbox.html"),
            HTML('<button type="submit" class="btn btn-primary"><span class="fas fa-compress"></span> Check Template for Errors</button>')
        )