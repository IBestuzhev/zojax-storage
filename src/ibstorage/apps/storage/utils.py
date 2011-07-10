from datetime import datetime

from django.http import HttpResponse
from django.utils import simplejson


def ajax_login_required(view_func):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated():
            return view_func(request, *args, **kwargs)
        json = simplejson.dumps({ 'login': True })
        return HttpResponse(json, mimetype='application/json')
    wrap.__doc__ = view_func.__doc__
    wrap.__dict__ = view_func.__dict__
    return wrap


def _ajax_encode(obj):
    if isinstance(obj, (datetime,)):
        return unicode(obj)


def ajaxify(view_func):
    def wrap(request, *args, **kwargs):
        resp = view_func(request, *args, **kwargs)
        if isinstance(resp, HttpResponse):
            return resp
        elif not isinstance(resp, dict):
            raise ValueError("ajaxify wrapped func should return dict or HTTPResponse")
        json = simplejson.dumps(resp, default=_ajax_encode)
        return HttpResponse(json, mimetype=resp.get('_type', 'application/json'))
    wrap.__doc__ = view_func.__doc__
    wrap.__dict__ = view_func.__dict__
    return wrap