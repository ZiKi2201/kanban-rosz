

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.formats import localize

from .forms import NewUserForm


@login_required
def home(request):
    all_tasks = []
    t_list = request.user.tasks.all()
    for t in t_list:
        t_dict = {
            'uuid': str(t.uuid),
            'name': t.name if t.name is not None else 'Отсутствует',
            'boardName': t.boardName,
            'date': str(localize(t.date)),
            'date_end': str(localize(t.date_end)) if t.date_end is not None else 'Отсутствует' ,
            'chief': t.chief.username if t.chief is not None else ' ',
            'date_update': str(localize(t.date_update)) if t.date_update is not None else 'Отсутствует',
            'comment': t.comment if t.comment is not None else 'Отсутствует',
            'attachments': [
                {
                    'id': a.id,
                    'url': request.build_absolute_uri(a.file.url),
                    'original_filename': a.original_filename,
                }
                for a in t.attachments.all()
            ],
        }
        all_tasks.append(t_dict)
    return render(request, 'index.html', {'tasks': all_tasks})


def register_request(request):
    if request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request,
                             'Аккаунт зарегистрирован: '
                             'добро пожаловать на сайт!')
            return redirect('board:login')
        messages.error(request, 'Не удалось зарегистрировать аккаунт. '
                                'Проверьте корректность данных и '
                                'попробуйте еще раз!')
    form = NewUserForm()
    return render(request=request,
                  template_name='register.html',
                  context={'register_form': form})


def login_request(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request,
                              f'Вы вошли на сайт под ником {username}.')
                return redirect('board:home')
            else:
                messages.error(request, 'Неверные имя и/или пароль.')
        else:
            messages.error(request, 'Неверные имя и/или пароль.')
    form = AuthenticationForm()
    return render(request=request, template_name='login.html',
                  context={'login_form': form})


def logout_request(request):
    logout(request)
    messages.info(request, 'Вы вышли из аккаунта.')
    return redirect('board:login')
