# Create your views here.
import socket

from django.contrib.auth import logout
from django.core.paginator import Paginator, InvalidPage
from django.core.urlresolvers import reverse
from django.middleware.csrf import get_token
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from storage.utils import ajax_login_required, ajaxify, ajax_redirect
from django.views.generic.base import TemplateView
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail, mail_admins
from boto.exception import S3ResponseError

from storage.models import UserFile
from storage.forms import UserFileForm, ShareForm


FROM_EMAIL = getattr(settings, 'DEFAULT_FROM_EMAIL', 'storage@ibstorage.com')

class IndexView(TemplateView):
    """A view to render index template
    """
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        # Add UserFileForm to pre-render it in default template
        ctx = super(IndexView, self).get_context_data(**kwargs)
        ctx['fileform'] = UserFileForm()
        return ctx

    def dispatch(self, request, *args, **kwargs):
        # Force updating CSRF cookie
        request.META["CSRF_COOKIE_USED"] = True
        return super(IndexView, self).dispatch(request, *args, **kwargs)


# Ajaxified views are rendered with PureJS template engine
# http://beebole.com/pure/
#
# Top level JSON keys are names of blocks that should be rendered with returned data
# For mapping of returned data to Pure templates check this files:
# * templates/index.html
# * static/js/storage.js
@ajax_login_required
@ajaxify
def list_files(request, page_num=1):
    """Return paginated list of all files
    View response is rendered with Pure template into filelist block.

    Expected output:
        emptyMsg - message when user has no files
        files - list of file objects with fields: file, link, uploaded_at, public
        pages - list of all pages (ie 1,2,3)
        cur_page - current page number
    """
    files = request.user.uploads
    resp = {}
    if not files.exists():
        resp['emptyMsg'] = "No files uploaded yet"
    resp['files'] = []
    pagination = Paginator(files.all(), 10)
    try:
        if page_num is None:
            page_num = 1
        page = pagination.page(page_num)
    except InvalidPage:
        page = pagination.page(1)
    for file in page.object_list:
        resp['files'].append({
            'file': file.get_file_name(),
            'link': reverse(fileinfo, kwargs={'id': file.id}),
            'uploaded_at': file.uploaded_at,
            'public': file.public
        })
    resp['pages'] = pagination.page_range
    resp['cur_page'] = page.number
    return {'filelist': resp, }


#@csrf_exempt
@ajax_login_required
@ajaxify
def upload(request):
    """Return Upload form validation results
    Pure block for this view is "fileupload"

    Form is pre-rendered with IndexView

    Expected output:
        errors - errors in upload form
        csrf_token - form on this page uses iFrame submit instead of AJAX
            So it's necessary to put csrf token to POST parameter, not header
    """
    # don't use direct access request.META.get('CSRF_COOKIE')
    # in this case django will NOT send a CSRF cookie. Use get_token function
    csrf_token = get_token(request)
    if request.method == "GET":
        return {"fileupload": {'csrf_token': csrf_token}}

    form = UserFileForm(request.POST, request.FILES)
    if form.is_valid():
        upload = form.save(commit=False)
        upload.user = request.user
        try:
            # Catch AWS communications errors
            upload.save()
            messages.info(request, "File was successfully uploaded")
        except (S3ResponseError, socket.error) as e:
            messages.error(request,
                           "Error saving your file, please try again later")
            mail_admins("S3 Connection error",
                        "%s\n Error occurred while uploading file. Check your AWS settings" % e)
        return {'redirect': '/list-files/', '_type': 'text/html'}
    return {'_type': 'text/html', "fileupload": {'errors': form.errors,
                                                 'csrf_token': csrf_token}}


@ajax_redirect
@ajaxify
def fileinfo(request, id):
    """Returns file info and possible file actions
    Pure block to render data is 'fileinfo'

    Expected output:
        errorMsg - File not found message
        file - current file name
        actions - list of file actions
        info - file metadata
    """
    try:
        user_file = UserFile.objects.get(id=int(id))
    except (ValueError, UserFile.DoesNotExist):
        return {'fileinfo': {'errorMsg': 'No such file'}}

    if not (user_file.public or user_file.user == request.user):
        return {'fileinfo': {'errorMsg': 'This file is protected'}}

    actions = [{'action': 'View', 'local': False, 'url': user_file.file.url}]
    if user_file.suitable_for_gdocs():
        actions.append(
                {'action': 'View with Google Docs Viewer', 'url': user_file.get_gdocs_url(request.build_absolute_uri),
                 'local': False})

    if user_file.user == request.user:
        actions.append({'action': 'Change public', 'url': reverse(change_publish, kwargs={'id': id}), 'local': True})
        if user_file.public:
            actions.append({'action': 'Share', 'url': reverse(share, kwargs={'id': id}), 'local': True})
        actions.append({'action': 'Delete', 'url': reverse(delete, kwargs={'id': id}), 'local': True})

    info = [
            {'name': 'status', 'value': 'public' if user_file.public else 'private'},
            {'name': 'author', 'value': user_file.user.username},
            {'name': 'uploaded', 'value': user_file.uploaded_at}]

    return {'fileinfo': {
        'file': user_file.get_file_name(),
        'actions': actions,
        'info': info
    }}


#@csrf_exempt
@ajax_login_required
@ajaxify
def share(request, id):
    """Shows share options for file
    Pure block to render data is "sharebox"

    Expected output:
        absolute_link - absolute link to this file (direct link)
        link - link to manage this file (ajax link)
        action - form action to submit
        form - complete form HTML withou <form> and <input type="submit"> tags
        file - current file name
    """
    try:
        user_file = UserFile.objects.get(id=int(id))
    except (ValueError, UserFile.DoesNotExist):
        return {'redirect': '/'}

    form = ShareForm(request.POST or None)
    file_link = reverse(fileinfo, kwargs={'id': id})
    if form.is_valid():
        msg = "Your friend %s shares a file with you:\n%s" % (
            user_file.user.username,
            request.build_absolute_uri(file_link)
            )
        if form.cleaned_data['message']:
            msg = "%s\n\nHis/her comments:\n%s" % (msg, form.cleaned_data['message'])

        send_mail("Check this file", msg, FROM_EMAIL, form.cleaned_data['emails'], fail_silently=True)
        messages.info(request, "Your mail was sent to %s" % ','.join(form.cleaned_data['emails']))
        return {'redirect': file_link, '_type': 'text/html'}

    return {'sharebox': {
        'absolute_link': request.build_absolute_uri(file_link),
        'link': file_link,
        'action': request.path,
        'form': form.as_p(),
        'file': user_file.get_file_name()
    }}


#@csrf_exempt
@ajax_login_required
@ajaxify
def change_publish(request, id):
    """View to change file public status
    Not public files are visible only to owner
    Pure block to render data is "publish"

    Expected output:
        status - current file status (as text)
        action_link - form action to submit
        back_link - link to manage this file
        file - current file name
    """
    if not request.is_ajax():
        return redirect('/')
    try:
        user_file = UserFile.objects.get(id=int(id))
    except (ValueError, UserFile.DoesNotExist):
        return {'redirect': '/'}

    if user_file.user == request.user:
        if request.method == "POST":
            user_file.public = not user_file.public
            user_file.save()
            messages.info(request, "File published status changed")
            return {'redirect': reverse(fileinfo, kwargs={'id': id})}

        return {'publish': {
            'status': 'public' if user_file.public else 'private',
            'action_link': request.path,
            'back_link': reverse(fileinfo, kwargs={'id': id}),
            'file': user_file.get_file_name()
        }}
    return {'redirect': '/'}


#@csrf_exempt
@ajax_login_required
@ajaxify
def delete(request, id):
    """Delete file with ajax interface
    On GET shows confirmation form, on POST deletes file.
    Pure block to render data is "filedelete"

    Expected output:
        action_link - form action to submit
        back_link - link to manage this file
        file - current file name
    """
    if not request.is_ajax():
        return redirect('/')
    try:
        user_file = UserFile.objects.get(id=int(id))
    except (ValueError, UserFile.DoesNotExist):
        return {'redirect': '/'}

    if user_file.user == request.user:
        if request.method == "POST":
            user_file.delete()
            messages.info(request, "File was deleted")
            return {'redirect': '/'}

        return {'filedelete': {
            'action_link': request.path,
            'back_link': reverse(fileinfo, kwargs={'id': id}),
            'file': user_file.get_file_name()
        }}
    return {'redirect': '/'}


@ajaxify
def ajax_logout(request):
    """Logout user with ajax request
    """
    logout(request)
    return {'redirect': '/'}