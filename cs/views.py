from io import TextIOWrapper
from django.http import HttpResponseRedirect
from django.shortcuts import render

from cs.forms import UploadFileFormCheque
from cs.models import ChequeImport
import pandas as pd


# Create your views here.
def upload_file(request):  # function allows the uploading of file from cheque import form
    if request.method == 'POST':
        form = UploadFileFormCheque(request.POST, request.FILES)
        if form.is_valid():
            stored_file_instance = ChequeImport(TextIOWrapper(request.FILES['file'], encoding="utf-8", newline=""))
            stored_file_instance.save()
            return HttpResponseRedirect('/cheque/importfile/uploads')
    else:
        form = UploadFileFormCheque()
    return render(request, 'upload_csv.html', {'form': form})


def parse_csv_file(csv_file):  # json_file is the returned file uploaded by upload_file function
    data_parsed = pd.read_csv(csv_file)
    return data_parsed


"""if __name__ == '__main__':
    store_file = upload_file(request)[1]
    data_parsed = parse_csv_file(store_file)
    print(data_parsed[1])"""