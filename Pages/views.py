from django.shortcuts import render

# Create your views here.


def index(request):
    return render(request, 'pages/index-new.html')


def test_ws(request):
    return render(request, 'test_channel.html')
