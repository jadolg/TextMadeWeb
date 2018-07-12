from pprint import pprint

import html2text
import markdown
import re
import requests
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from google import google

PAGE_BOTTOM = '''<div style="margin: auto;
    width: 13%;
    border: 3px solid dodgerblue;
    padding: 10px;">
    <h3>Text Made Web</h3>
    <p>Making the web smaller</p>
    <p>Go <a href="/">Home</a></p>
    <p>Fork me on <a target="_blank" href="https://github.com/jadolg/TextMadeWeb">GitHub</a><p>
</div>
'''


def home(request):
    if request.method == 'POST' and 'url' in request.POST:
        return HttpResponseRedirect('/t/' + request.POST['url'])
    return render(request, 'home.html')


def remove_img_md(data):
    p = re.compile(r'!\s*\[.*?\]\(.*?\)', re.DOTALL)
    return p.sub('', data)


def remove_jumps(data):
    ndata = data
    p = re.compile(r'\[(.*?)\]', re.DOTALL)
    for i in p.findall(ndata):
        ndata = ndata.replace('[' + i + ']', '[' + i.replace('\n', ' ') + ']')

    p = re.compile(r'\((.*?)\)', re.DOTALL)
    for i in p.findall(ndata):
        ndata = ndata.replace('(' + i + ')', '(' + i.replace('\n', '') + ')')

    return ndata


def insert_cleaner_url(data, url):
    newdata = data
    urls = []
    p = re.compile(r'\(http://(.*?)\)', re.DOTALL)
    for i in p.findall(data):
        if 'http://' + i not in urls:
            urls.append('http://' + i)

    p = re.compile(r'\(https://(.*?)\)', re.DOTALL)
    for i in p.findall(data):
        if 'https://' + i not in urls:
            urls.append('https://' + i)

    for i in urls:
        try:
            newdata = re.sub('(' + url + '/t/)?' + i, url + '/t/' + i, newdata)
        except:
            print('failed for', i)

    return newdata


def textify_it(request, url):
    if url.startswith('http://') or url.startswith('https://'):
        try:
            page = requests.get(url, verify=False, allow_redirects=True)
        except:
            return render(request, 'home.html', {'message': 'There was an error trying to open ' + url})
        if page.status_code == 200:
            page = str(page.text)
        else:
            return render(request, 'home.html',
                          {'message': "I'm unable to textify this page. Error code " + str(page.status_code)})

        try:
            title = ''
            t = re.findall('<title>(.*?)</title>', page, re.IGNORECASE)
            if len(t) > 0:
                title = '<head><title>' + t[0] + ' | Text Made Web</title></head>'
            md = html2text.html2text(page, bodywidth=0, baseurl=url)
            md = remove_jumps(md)
            md = remove_img_md(md)
            md = insert_cleaner_url(md, get_url(request))

            return HttpResponse(title + '<body><h2>' + t[0] + '</h2><h4><a href="' + url + '">' + url + '</a></h4>'
                                + markdown.markdown(md) + PAGE_BOTTOM + '<body>')
        except:
            return render(request, 'home.html',
                          {'message': 'I was unable to textify this page :\'('})
    else:
        try:
            search_results = google.search(url, 3)
            return render(request, 'search_results.html',
                          {'results': search_results, 'baseurl': get_url(request), 'q': url})
        except:
            return render(request, 'home.html',
                          {'message': "There has being an error while searching :'("})


def md_it(request, url):
    page = requests.get(url, verify=False, allow_redirects=True).text
    md = html2text.html2text(page, bodywidth=0, baseurl=url)
    # result = '<p>' + '</p><p>'.join(md.split('\n')) + '</p>'
    return HttpResponse(md)


def get_url(request):
    url = ''
    if request.is_secure():
        url += 'https://'
    else:
        url += 'http://'

    url += request.get_host()

    return url
