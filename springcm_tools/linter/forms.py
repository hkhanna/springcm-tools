from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Layout, Div, Field

class UploadFileForm(forms.Form):
    file = forms.FileField(label="Upload SpringCM Template (.docx)")

    def __init__(self, *args, **kwargs):
        super(UploadFileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.form_action = 'linter:index'
        self.helper.layout = Layout(
            Div('file'),
            HTML('<hr /><button type="submit" class="btn btn-primary"><span class="fas fa-compress"></span> Check for Errors</button>')
        )