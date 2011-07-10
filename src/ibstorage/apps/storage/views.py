# Create your views here.
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from storage.utils import ajax_login_required, ajaxify
from django.utils import simplejson

from storage.models import UserFile

@ajax_login_required
@ajaxify
def list_files(request):
    files = request.user.uploads
    resp = {}
    if not files.exists():
        resp['emptyMsg'] = "No files uploaded yet"
    resp['files'] = []
    for file in files.values('file', 'uploaded_at', 'public', 'id'):
        resp['files'].append({
            'file': file['file'],
            'link': "file/%d" % file['id'],
            'uploaded_at' : file['uploaded_at'],
            'is_public' : 'public' if file['public'] else '',
        })
        
    return {'filelist' : resp}

@csrf_exempt
@ajax_login_required
@ajaxify
def upload(request):
    if request.method == "GET":
        return {"fileupload":True}

    print request.POST, request.FILES
    if 'file_upload' in request.FILES:
        uf = UserFile(user=request.user)
        uf.file = request.FILES['file_upload']
        uf.save()

    return {'redirect':'/list-files/', '_type':'text/html'}