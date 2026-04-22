from django.shortcuts import render


def home(request):
    context = {
        'title': 'Головна сторінка',
        'message': 'Це головна сторінка лабораторної роботи 3',
    }
    return render(request, 'myapp/home.html', context)


def page1(request):
    context = {
        'title': 'Сторінка 1',
        'message': 'Це контент першої сторінки, переданий через context',
    }
    return render(request, 'myapp/page1.html', context)


def page2(request):
    context = {
        'title': 'Сторінка 2',
        'message': 'Це контент другої сторінки, переданий через context',
    }
    return render(request, 'myapp/page2.html', context)