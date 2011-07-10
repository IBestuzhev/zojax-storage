import re

from django import forms
from django.core.validators import validate_email
from storage.models import UserFile

class UserFileForm(forms.ModelForm):
    class Meta:
        model = UserFile
        fields = ('file', 'public')


email_separator_re = re.compile(r'[^\w\.\-\+@_]+')


class EmailsListField(forms.CharField):
    """http://djangosnippets.org/snippets/1958/
    """
    widget = forms.Textarea(attrs={'rows':3})

    def clean(self, value):
        super(EmailsListField, self).clean(value)

        emails = email_separator_re.split(value)

        if not emails:
            raise forms.ValidationError(_(u'Enter at least one e-mail address.'))

        map(validate_email, emails)

        return emails


class ShareForm(forms.Form):
    emails = EmailsListField(help_text="Enter one mail per line")
    message = forms.CharField(widget=forms.Textarea(), required=False)