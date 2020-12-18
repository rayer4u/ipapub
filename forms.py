from django import forms
from .models import UpFile


class UploadModelFileForm(forms.ModelForm):
    class Meta:
        model = UpFile
        exclude = ('pub', 'plist', 'status', 'up_date', 'from_ip')
