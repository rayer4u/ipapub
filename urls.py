from django.urls import path
from django.views.generic import FormView
from .views import upload, AllView, OneView
from .forms import UploadModelFileForm


urlpatterns = [
    path('', upload, name='upload'),
    path('all', AllView.as_view(), name='all'),
    path('<path>', OneView.as_view(), name='one'),
]
