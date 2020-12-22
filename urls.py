from django.urls import path, re_path
from django.views.generic import FormView
from .views import upload, AllView, OneView
from .forms import UploadModelFileForm


urlpatterns = [
    path('', upload, name='upload'),
    path('all', AllView.as_view(), name='all'),
    re_path('^(?P<path>.*)$', OneView.as_view(), name='one'),  # 需要读取多段路径，只能采用re_path
]
