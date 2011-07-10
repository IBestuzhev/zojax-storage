import os.path
import urllib

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_delete

from storages.backends.s3boto import S3BotoStorage
from django.conf import settings


#Check if S3 storage is enabled in settings
if getattr(settings, "AWS_ACCESS_KEY_ID", False) and getattr(settings, "AWS_SECRET_ACCESS_KEY", False):
    Storage = S3BotoStorage()
else:
    Storage = None
VIEW_IN_GDOCS = getattr(settings, 'VIEW_IN_GDOCS', ('.pdf', '.doc'))

# Create your models here.
def get_user_upload_dir(user_file, filename):
    return "%s/%s" % (user_file.user.username, filename)


class UserFile(models.Model):
    """ Model that handle file uploaded by user
    """
    user = models.ForeignKey(User, related_name="uploads")
    file = models.FileField(upload_to=get_user_upload_dir, storage=Storage)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    public = models.BooleanField(default=False, help_text="Allows you to share file")

    def suitable_for_gdocs(self):
        """Checks that uploaded file can be viewed in Google Docs Viewer
        Check is based on file extension

        returns bool
        """
        ext = os.path.splitext(self.file.name)[1]
        return ext.lower() in VIEW_IN_GDOCS

    def get_gdocs_url(self, absolutizer=None):
        """Get the URL to view uploaded file in Google Docs Viewer
        absolutizer - callable that converts FieldFile.url value to absolute url
            it's intended to be used with default Django FileStorage
            common usage is to pass request.build_absolute_uri
        """
        url = self.file.url
        if callable(absolutizer):
            url = absolutizer(url)
        return "http://docs.google.com/viewer?%s" % urllib.urlencode({'url': url})

    def __unicode__(self):
        return unicode(self.file)

    def get_file_name(self):
        """Returns only file name without any path component
        """
        return os.path.split(self.file.name)[-1]


def delete_handler(instance, using=None, **kwargs):
    """ Handler that deletes file on deleting UserFile instance
    """
    instance.file.delete(save=False)

pre_delete.connect(delete_handler, sender=UserFile, dispatch_uid='file_delete_handler')