from django.shortcuts import render
from django.http import HttpResponse, Http404

from .forms import UploadFileForm

def index(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            # TODO: store file
            # TODO: lint
            return HttpResponse("Success!")
    else:
        form = UploadFileForm()

    return render(request, 'linter/index.html', {'form': form})
