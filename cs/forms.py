from django import forms


class UploadFileFormCheque(forms.Form):  # class where the file is uploaded
    title = forms.CharField(max_length=50)
    file = forms.FileField(required=False, widget=forms.FileInput(attrs={'class': 'form-control', 'placeholder':
        'Upload "ExempleExportCheque.csv"', 'help_text': 'Choose a .csv file with cheque to enter'}))
