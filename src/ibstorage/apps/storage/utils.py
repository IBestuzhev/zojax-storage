from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.context import RequestContext
from django.utils import simplejson
from django.conf import settings
from django.contrib.messages.storage.base import Message

STATE_SEPARATOR = getattr(settings, 'STATE_SEPARATOR', '#!')

def ajax_login_required(view_func):
    """Decorator for ajax views that checks that user is logged in.
    Returns either view response or { 'login': True } json string
    """
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated():
            return view_func(request, *args, **kwargs)
        json = simplejson.dumps({ 'login': True })
        return HttpResponse(json, mimetype='application/json')
    wrap.__doc__ = view_func.__doc__
    wrap.__dict__ = view_func.__dict__
    return wrap


def _ajax_encode(obj):
    """Helper that try to convert some values to JSON serializable format
    """
    if isinstance(obj, Message):
        return {'tags' : obj.tags, 'message' : unicode(obj)}
    elif isinstance(obj, (datetime,)):
        return unicode(obj)


def ajaxify(view_func):
    """Decorator for views to work with ajax requests
    View can return HttpResponse object or dict.
    HttpResponse will be passed without processing, dict will be
    returned as json

    Also adds messages list from django message framework.
    And adds instructions.username if user is logged in

    Default mimetype is application/json.
    it can be overwritten with _type key in dictionary.
    """
    def wrap(request, *args, **kwargs):
        resp = view_func(request, *args, **kwargs)
        if isinstance(resp, HttpResponse):
            return resp
        elif not isinstance(resp, dict):
            raise ValueError("ajaxify wrapped func should return dict or HTTPResponse")
        request_context = RequestContext(request)
        if 'messages' not in resp and 'redirect' not in resp:
            resp['messages'] = list(request_context['messages'])
        if request.user.is_authenticated():
            resp['instructions'] = {'username' : request.user.username}
        json = simplejson.dumps(resp, default=_ajax_encode)
        return HttpResponse(json, mimetype=resp.get('_type', 'application/json'))
    wrap.__doc__ = view_func.__doc__
    wrap.__dict__ = view_func.__dict__
    return wrap


def ajax_redirect(view_func):
    """Redirects direct deep link to the deep link with #!/
    i.e. http://example.com/file/5/
    becames
    http://example.com/#!/file/5/
    """
    def wrap(request, *args, **kwargs):
        if request.is_ajax():
            return view_func(request, *args, **kwargs)
        else:
            return redirect('/%s%s'%(STATE_SEPARATOR, request.path))
    wrap.__doc__ = view_func.__doc__
    wrap.__dict__ = view_func.__dict__
    return wrap