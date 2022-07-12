from django import forms


class UploadFileFormCheque(forms.Form):  # class where the file is uploaded
    title = forms.CharField(max_length=50)
    file = forms.FileField()
