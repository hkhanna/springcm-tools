from django.shortcuts import render
from django.http import HttpResponse, Http404

from .forms import UploadFileForm
from .utils import lint, Document

def index(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            return index_uploaded(request)
    else:
        form = UploadFileForm()

    return render(request, 'linter/index.html', {'form': form})

def index_uploaded(request):
    # TODO: store file
    document = Document(request.FILES['file'])
    doc_errors = lint(document)
    return render(request, 'linter/index_uploaded.html', { 'doc_errors': doc_errors })