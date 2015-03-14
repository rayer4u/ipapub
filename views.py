#coding:utf-8
from __future__ import print_function

from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
from django.http import Http404
from django.http import HttpResponseRedirect
from django.core.files import File
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from os.path import abspath,dirname,join,basename,exists,splitext
from uuid import uuid4

import os
import json
import urlparse
import subprocess
import shutil
import re
import ipapub
import zipfile
import sys

from forms import UploadModelFileForm
from models import UpFile

rule_repl = re.compile(r"(\{\{)(.*)(\}\})")

@csrf_exempt  #for post out of html
def upload(request):
    if request.method == 'POST':
        form = UploadModelFileForm(request.POST, request.FILES)
        if form.is_valid():
            o = form.save(commit=False)
            
            #path检查
            path_rela = join(ipapub.PACKAGE_DIR, o.path)+'.ipa' #realative to MEDIA_ROOT
            path_full = join(settings.MEDIA_ROOT, path_rela)

            if exists(path_full):
                return HttpResponse(json.dumps({'err':'existed'}), content_type="application/json")
            if not exists(dirname(path_full)):
                os.makedirs(dirname(path_full))
            
            sign = False
            on = ''
            if o.file:
                if o.signed:
                    return HttpResponse(json.dumps({'err':'have file not sign'}), content_type="application/json")
                sign = True
                on = o.file.name  #origin file name
            else:
                if not o.signed:
                    return HttpResponse(json.dumps({'err':'signed or file must have one'}), content_type="application/json")
                
            current_uri = '%s://%s' % ('https' if request.is_secure() else 'http',
                             request.get_host())
            
            #保存
            o.from_ip = request.POST['from'] if not sign and 'from' in request.POST  else get_client_ip(request)
            o.status = 'uploaded'
            o.save()

            tmpdir = join(dirname(__file__), uuid4().hex)
            os.mkdir(tmpdir)

            #解包
            if sign:
                unsignedapp = o.file.path
                signedipa = path_full
    
                
                cmd_tar = r'tar -xzf %s -C %s' % (unsignedapp, tmpdir)
                p = subprocess.Popen(cmd_tar, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=os.environ, shell=True)
                out, err = p.communicate()
                if len(err) > 0:
                    o.status = 'untarfail'
                    o.save()
                    shutil.rmtree(tmpdir)
                    return HttpResponse(json.dumps({'err':o.status}), content_type="application/json")
    
                #签名.remove tgz  ext
                tmpapp = join(tmpdir, splitext(on)[0])
#                 cmd_sign = 'echo test > '+path_full
                cert,key = request.POST['certification'].split(':')
                cmd_sign = 'xcrun -sdk iphoneos PackageApplication -v %s -o %s --sign "%s" --embed "%s"' \
                    %(tmpapp, path_full, ipapub.CERTS[cert][key], join(ipapub.PROFILES_DIR, cert, request.POST['id'], request.POST['profile']))
                p = subprocess.Popen(cmd_sign, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                out, err = p.communicate()
                
                if len(err) > 0:
                    o.status = 'signfail'
                    o.save()
                    shutil.rmtree(tmpdir)
                    return HttpResponse(json.dumps({'err':o.status, 'cmd':cmd_sign}), content_type="application/json")
                o.signed.name = path_rela  
                o.save()
            
            #plist
            path_plist_rela = splitext(path_rela)[0]+'.plist'
            path_plist_full = join(settings.MEDIA_ROOT, path_plist_rela)
            f = open(path_plist_full, 'w+')
            gens = {"ipaurl":urlparse.urljoin(current_uri, join(settings.MEDIA_URL, path_rela)),
                    "iconsmallurl":urlparse.urljoin(current_uri, join(settings.MEDIA_URL, o.icons.url)),
                    "iconbigurl":urlparse.urljoin(current_uri, join(settings.MEDIA_URL, o.iconb.url)),
                    }
            f.write(rule_repl.sub(lambda mt:gens[mt.group(2).lower()] if mt.group(2).lower() in gens else mt.group(1)+mt.group(2)+mt.group(3), request.POST['plist']).encode('utf-8'))
            f.close()
            o.plist.name = path_plist_rela
            o.save()

            if 'ipaurl' in request.POST:
                #need publish package
                path_plist_full = join(tmpdir, splitext(basename(path_rela))[0]+'.plist')
                f = open(path_plist_full, 'w+')
                gens = {"ipaurl":request.POST['ipaurl'],
                        "iconsmallurl":request.POST['iconsmallurl'] if 'iconsmallurl' in request.POST else '',
                        "iconbigurl":request.POST['iconbigurl'] if 'iconbigurl' in request.POST else '',
                        }
                f.write(rule_repl.sub(lambda mt:gens[mt.group(2).lower()] if mt.group(2).lower() in gens else mt.group(1)+mt.group(2)+mt.group(3), request.POST['plist']).encode('utf-8'))
                f.close()

                path_zip_rela = splitext(path_rela)[0]+'.zip'
                path_zip_full = join(settings.MEDIA_ROOT, path_zip_rela)
                #not support by 2.6
#                 with zipfile.ZipFile(path_zip_full, 'w') as myzip:
                try:
                    myzip = zipfile.ZipFile(path_zip_full, 'w')
                    myzip.write(path_plist_full, (basename(request.POST['plisturl']) if 'plisturl' in request.POST else basename(path_plist_full)))
                    myzip.write(path_full, basename(gens['ipaurl']))
                    if gens['iconsmallurl'] != '':
                        myzip.write(join(settings.MEDIA_ROOT, o.icons.path), basename(gens['iconsmallurl'])) 
                    if gens['iconbigurl'] != '':
                        myzip.write(join(settings.MEDIA_ROOT, o.iconb.path), basename(gens['iconbigurl'])) 
                    myzip.close()
                except Exception, e:
                    print(e, file=sys.stderr)
                    o.status = 'pubfail'
                    o.save()
                    shutil.rmtree(tmpdir)
                    return HttpResponse(json.dumps({'err':str(e)}), content_type="application/json")                    
                
                o.pub.name = path_zip_rela  
                o.save()
                                            
            o.status = 'success'
            o.save()
            shutil.rmtree(tmpdir)

            #保存列表
            form.save_m2m()


            result = {"url":urlparse.urljoin(current_uri, join(request.path, o.path))}
        else:
            result = {"err":dict(form.errors)};
        return HttpResponse(json.dumps(result), content_type="application/json")
    else:
        form = UploadModelFileForm()
        
    return render(request, 'ipapub/upload.html', {'form': form})

class AllView(ListView):
    template_name="ipapub/upfile_list.html"
    paginate_by = 20
    
    def get_queryset(self):
        return UpFile.objects.order_by("-up_date")
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ListView, self).get_context_data(**kwargs)
        # Add in the publisher
        context['request'] = self.request
        return context

class OneView(DetailView):
    model = UpFile
    slug_field = 'path'
    slug_url_kwarg = 'path'
    
    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        # Add in the publisher
        context['basedir'] = '%s://%s' % ('https' if self.request.is_secure() else 'http',
                             self.request.get_host())        
        return context
    
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
