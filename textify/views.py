import html2text
import markdown
import re
import requests
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render


def home(request):
    if request.method == 'POST' and 'url' in request.POST:
        return HttpResponseRedirect('/t/'+request.POST['url'])
    return render(request, 'search.html')


def remove_img_md(data):
    p = re.compile(r'!\s*\[.*?\]', re.DOTALL)
    return p.sub('[image]', data)


def remove_jumps(data):
    ndata = data
    p = re.compile(r'\[(.*?)\]', re.DOTALL)
    for i in p.findall(ndata):
        ndata = ndata.replace('['+i+']', '['+i.replace('\n', ' ')+']')

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
            urls.append('http://'+i)

    p = re.compile(r'\(https://(.*?)\)', re.DOTALL)
    for i in p.findall(data):
        if 'https://'+i not in urls:
            urls.append('https://'+i)

    for i in urls:
        try:
            newdata = re.sub('('+url+'/t/)?'+i, url+'/t/' + i, newdata)
        except:
            print('failed for', i)

    return newdata


def textify_it(request, url):
    try:
        page = requests.get(url, verify=False)
    except:
        return render(request, 'search.html', {'message': 'There was an error trying to open '+url})
    if page.status_code == 200:
        page = page.text
    else:
        return render(request, 'search.html', {'message': "I'm unable to textify this page. Error code "+str(page.status_code)})

    md = html2text.html2text(page, bodywidth=0, baseurl=url)
    md = remove_img_md(md)
    md = insert_cleaner_url(md, get_url(request))
    md = remove_jumps(md)
    return HttpResponse(markdown.markdown(md))


def md_it(request, url):
    page = requests.get(url, verify=False).text
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
