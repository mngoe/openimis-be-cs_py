from django.core.checks import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from cs.forms import UploadFileFormCheque
from cs.models import ChequeImport
import pandas as pd


# Create your views here.
def upload_file(request):  # function allows the uploading of file from cheque import form
    if request.method == 'POST':
        form = UploadFileFormCheque(request.POST, request.FILES)
        if form.is_valid():
            stored_file_instance = ChequeImport(stored_file=request.FILES['file'])
            stored_file_instance.save()
            stored_data_csv = stored_file_instance.stored_file
            response_http = HttpResponseRedirect('/cheque/importfile/uploads')
            return {1: stored_data_csv, 2: response_http}
    else:
        form = UploadFileFormCheque()
    return render(request, 'upload_csv.html', {'form': form})


def parse_csv_file(csv_file):  # json_file is the returned file uploaded by upload_file function
    data_parsed = pd.read_csv(csv_file)
    return data_parsed


