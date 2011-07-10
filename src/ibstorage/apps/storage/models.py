from django.db import models
from django.contrib.auth.models import User

# Create your models here.
def get_user_upload_dir(user_file, filename):
    return "%s/%s" % (user_file.user.username, filename)


class UserFile(models.Model):
    user = models.ForeignKey(User, related_name="uploads")
    file = models.FileField(upload_to=get_user_upload_dir)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    public = models.BooleanField(default=False)
