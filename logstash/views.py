# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404, HttpResponse, HttpResponseForbidden, HttpResponseNotFound
from django.utils.encoding import smart_str
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.db import connections
from django.core.paginator import InvalidPage, EmptyPage, Paginator
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.contrib import messages

from servers.models import Server
from logstash.models import File, Execution
from logstash.forms import FileForm
from logstash.tasks import do_autodetection

import json


@login_required
@staff_member_required
def file_list(request):
    """Show the home page with the list of monitored files"""

    liste = File.objects.order_by('file').all()

    return render_to_response('logstash/files/list.html', {'liste': liste}, context_instance=RequestContext(request))


@login_required
@staff_member_required
def file_show(request, pk):
    """Show details of an file"""

    object = get_object_or_404(File, pk=pk)

    return render_to_response('logstash/files/show.html', {'object': object}, context_instance=RequestContext(request))


@login_required
@staff_member_required
def file_edit(request, pk):
    """Edit an file"""

    try:
        object = File.objects.get(pk=pk)
    except:
        object = File()

    if request.method == 'POST':  # If the form has been submitted...
        form = FileForm(request.POST, instance=object)

        if form.is_valid():  # If the form is valid
            object = form.save()

            messages.success(request, 'The file has been saved.')

            return redirect(reverse('logstash.views.file_list'))
    else:
        form = FileForm(instance=object)

    tags = []

    for f in File.objects.all():
        for t in f.tags.split(','):
            if t not in tags:
                tags.append(t)

    return render_to_response('logstash/files/edit.html', {'form': form, 'tags': tags}, context_instance=RequestContext(request))


@login_required
@staff_member_required
def file_delete(request, pk):
    """Delete an file"""

    object = get_object_or_404(File, pk=pk)

    object.delete()

    messages.success(request, 'File has been deleted.')

    return redirect(reverse('logstash.views.file_list', args=()))


def generate_config(request, name):
    """Generate logstash shipper config"""

    server = get_object_or_404(Server, logstash_shipper=True, name=name)

    config = """input {

  """

    for file in server.file_set.all():
        config += """file {
    type => \"""" + file.type + """\"
    path => [ \"""" + file.file + """\" ]
    tags => [ """ + ','.join(['"' + x + '"' for x in file.tags.split(',')]) + """ ]
    sincedb_path => "/var/cache/logstash/.sincedb"
  }
"""

    config += """
}

filter {
  if [type] == "apachelog" {
    grok {
      match => { "message" => "%{IPORHOST:clientip} %{USER:ident} %{USER:auth} \[%{HTTPDATE:timestamp}\] \\"(?:%{WORD:verb} %{URIPATHPARAM:request}(?: HTTP/%{NUMBER:httpversion})?|-)\\" %{NUMBER:response} (?:%{NUMBER:bytes}|-)" }
    }

    date {
      match => { "timestamp" => "dd/MMM/yyyy:HH:mm:ss Z" }
    }
  }

  if [type] == "syslog" {

    grok {
      pattern => [ "%{SYSLOGTIMESTAMP:syslog_timestamp} %{SYSLOGHOST:syslog_hostname} %{DATA:syslog_program}(?:\\[%{POSINT:syslog_pid}\\])?: %{GREEDYDATA:syslog_message}" ]
      add_field => [ "received_at", "%{@timestamp}" ]
      }

      date {
        match => [ "syslog_timestamp", "MMM  d HH:mm:ss", "MMM dd HH:mm:ss" ]
      }
      if !("_grokparsefailure" in [tags]) {
        mutate {
            replace => [ "@source_host", "%{syslog_hostname}" ]
            replace => [ "message", "%{syslog_message}" ]
        }
      }

      mutate {
          remove => [ "syslog_hostname", "syslog_message", "syslog_timestamp" ]
      }
  }

  if [type] == "nginxlog" {
    grok {
      match => { "message" => "%{IPORHOST:clientip} %{GREEDYDATA:ident} %{GREEDYDATA:auth} \\[%{HTTPDATE:timestamp}\\] \\"%{WORD:verb} %{URIPATHPARAM:request} HTTP/%{NUMBER:httpversion}\\" %{NUMBER:response}  (?:%{NUMBER:bytes}|-) (?:\\"(?:%{URI:referrer}|-)\\"|%{QS:referrer}) %{QS:agent} %{QS:xforwardedfor} %{IPORHOST:host} %{BASE10NUM:request_duration}" }
    }

    date {
      match => { "timestamp" => "dd/MMM/yyyy:HH:mm:ss Z" }
    }
  }

  if [type] == "nginxerrlog" {
    grok {
      match => { "message" => "%{DATESTAMP:timestamp} %{GREEDYDATA:message}, client: %{IP:clientip}, server: %{IPORHOST:host}, request: \\"%{WORD:verb} %{URIPATHPARAM:request} HTTP/%{NUMBER:httpversion}\\", upstream: \\"%{URI:upstream}\\", host: \\"%{IPORHOST:host}\\", referrer: \\"%{URI:referrer}\\"" }
    }

    date {
      match => { "timestamp" => "yyyy/mm/dd HH:mm:ss" }
    }
  }

}

output {
  redis { host => \"""" + settings.LOGSTASH_SERVER + """\" data_type => "list" key => "logstash" }
}
"""
    return HttpResponse(config)


@login_required
@staff_member_required
def start_autodetect(request):
    """Start automatic detection"""

    e = Execution()
    e.save()

    do_autodetection.delay(e.pk)

    return redirect(reverse('logstash.views.watch_autodetect', args=(e.pk,)))


@login_required
@staff_member_required
def watch_autodetect(request, key):
    """Watch automatic detection"""

    ex = get_object_or_404(Execution, pk=key)

    return render_to_response('logstash/autodetect/watch.html', {'ex': ex}, context_instance=RequestContext(request))


@login_required
@staff_member_required
def watch_get_status(request, key):
    """Return current status about automatic detection"""

    ex = get_object_or_404(Execution, pk=key)

    sta = 'd' if ex.done else 'r'

    return HttpResponse(sta + ex.output)


@login_required
@staff_member_required
def watch_final(request, key):
    """Final step for automatic detection: Display results and save"""

    ex = get_object_or_404(Execution, pk=key)

    if request.method == 'POST':

        for elem in request.POST.getlist('todel[]'):
            File.objects.get(pk=elem).delete()

        for elem in request.POST.getlist('toadd[]'):
            file, type, tags, server_pk = json.loads(elem)
            server = Server.objects.get(pk=server_pk)

            File(file=file, type=type, tags=tags, server=server).save()

        messages.success(request, 'The file list has been updated !')
        return redirect(reverse('logstash.views.file_list'))

    toadd = []
    todel = []

    data = json.loads(ex.sugested_result)

    for elem in data:
        toadd.append(json.dumps(elem))

    for file in File.objects.all():
        json_repr = json.dumps((file.file, file.type, file.sorted_tags(), file.server.pk))

        if json_repr in toadd:
            toadd.remove(json_repr)
        else:
            todel.append(file)

    toadd_with_data = []

    for elem in toadd:
        file, type, tags, server_pk = json.loads(elem)
        server = Server.objects.get(pk=server_pk)

        toadd_with_data.append((file, type, tags, server, elem))

    return render_to_response('logstash/autodetect/final.html', {'ex': ex, 'toadd': toadd_with_data, 'todel': todel}, context_instance=RequestContext(request))
