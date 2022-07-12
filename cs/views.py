from django.http import HttpResponseRedirect
from django.shortcuts import render
from cs.forms import UploadFileFormCheque
from cs.models import ChequeImport


# Create your views here.
def upload_file(request):  # function allows the uploading of file from cheque import form
    if request.method == 'POST':
        form = UploadFileFormCheque(request.POST, request.FILES)
        if form.is_valid():
            stored_file_instance = ChequeImport(file_field=request.FILES['file'])
            stored_file_instance.save()
            return HttpResponseRedirect('/cheque/importfile/uploads')
    else:
        form = UploadFileFormCheque()
    return render(request, 'upload.html', {'form': form})
