from django.shortcuts import render, redirect

from parse_text.models import Document, Note
from parse_text.manager import read_and_save_file, get_weight_sentence


def parse_text(request):
    if request.method == 'POST':
        file = request.FILES['file']
        theme = request.POST['theme']
        document = read_and_save_file(file, theme)
        get_weight_sentence(document)
        return redirect('search')
    return render(request, 'parse_text/upload_file.html')


def index(request):
    documents = Document.objects.all()
    return render(request, 'parse_text/search_page.html', {'documents': documents})


def results(request, search_id):
    note = Note.objects.get(document_id=search_id)
    return render(request, 'parse_text/results_page.html', {'note': note})
