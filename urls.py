from django.conf.urls import patterns, include, url
from django.views.generic import FormView
from views import upload, AllView, OneView
from forms import UploadModelFileForm

urlpatterns = patterns('',
    url(r'^$', upload, name='upload'),
    url(r'^all', AllView.as_view(), name='all'), 
    url(r'^(?P<path>.*)$', OneView.as_view(), name='one'), 
)
