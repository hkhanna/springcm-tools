from datetime import datetime as dt
import os

from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.conf import settings

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
    uploaded_file = request.FILES['file']
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    now_str = dt.now().strftime('%Y%m%d%H%M%S')
    filename = now_str + '_' + uploaded_file.name
    with open(settings.UPLOAD_DIR + '/' + filename, 'wb') as f:
        for chunk in uploaded_file.chunks():
            f.write(chunk)

    document = Document(uploaded_file)
    doc_errors = lint(document)
    return render(request, 'linter/index_uploaded.html', { 'doc_errors': doc_errors })