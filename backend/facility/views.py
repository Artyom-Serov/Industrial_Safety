"""
Модуль представлений, управляющих проверками, аттестуемыми и комиссиями.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.views.generic import ListView
from .models import Examination
from .forms import ExaminationCreateForm, ExaminationUpdateForm


class IndexView(ListView):
    """
    Представление для отображения списка всех проверок. Отображает все
    записи для суперпользователей и только связанные с организацией
    текущего пользователя для других пользователей. Также поддерживает
    фильтрацию по различным параметрам: дате текущей проверки, дате следующей
    проверки, номеру курса, названию курса и цеху (участку).

    Параметры:
        - model: Модель, с которой работает представление (Examination).
        - template_name: Имя шаблона для отображения (facility/index.html).
        - context_object_name: Имя контекстной переменной для передаваемых
            данных ('examinations').
        - ordering: Сортировка списка (по убыванию даты создания).

    Возвращает:
        - queryset: Отфильтрованный и отсортированный список проверок.
    """
    model = Examination
    template_name = 'facility/index.html'
    context_object_name = 'examinations'
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Получает фильтрованный список проверок в зависимости от параметров
        запроса. Записи сортируются в зависимости от параметра 'order_by'.

        Параметры:
            - current_check_date: Фильтрация по текущей дате проверки.
            - next_check_date: Фильтрация по следующей дате проверки.
            - course_number: Фильтрация по номеру курса.
            - course_name: Фильтрация по названию курса.
            - brigade: Фильтрация по цеху (участку) аттестуемого.
            - order_by: Параметр сортировки (по умолчанию '-created_at').

        Возвращает:
            - queryset: Отфильтрованный и отсортированный список проверок.
        """
        user = self.request.user

        if not user.is_authenticated:
            return Examination.objects.none()

        cache_key = (f'examinations_{user.id}_filters_'
                     f'{self.request.GET.urlencode()}')
        queryset = cache.get(cache_key)
        if queryset is None:
            if user.is_superuser:
                queryset = Examination.objects.all()
            else:
                queryset = Examination.objects.filter(
                    examined__company_name=user.organization
                )

            current_check_date = self.request.GET.get('current_check_date')
            next_check_date = self.request.GET.get('next_check_date')
            course_number = self.request.GET.get('course_number')
            course_name = self.request.GET.get('course_name')
            brigade = self.request.GET.get('brigade')
            order_by = self.request.GET.get('order_by', '-created_at')

            if current_check_date:
                queryset = queryset.filter(
                    current_check_date=current_check_date
                )
            if next_check_date:
                queryset = queryset.filter(
                    next_check_date=next_check_date
                )
            if course_number:
                queryset = queryset.filter(
                    course__course_number__icontains=course_number
                )
            if course_name:
                queryset = queryset.filter(
                    course__course_name__icontains=course_name
                )
            if brigade:
                queryset = queryset.filter(
                    examined__brigade__icontains=brigade
                )

            queryset = queryset.order_by(order_by)
            cache.set(cache_key, queryset, timeout=settings.CACHE_TTL)

        return queryset


@login_required
def create_examination(request):
    """
    Представление для создания новой проверки. Обрабатывает форму создания
    проверки, сохраняет данные в базе данных и перенаправляет пользователя
    на главную страницу со списком проверок.

    Параметры:
        - request: Объект запроса, содержащий данные формы.

    Возвращает:
        - render: Отображает форму для создания проверки или перенаправляет
                  на страницу со списком проверок после успешного сохранения.
    """
    template = 'facility/examination_create_form.html'
    if request.method == 'POST':
        form = ExaminationCreateForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            cache.delete('examinations_*')
            return redirect('facility:index')
    else:
        form = ExaminationCreateForm(user=request.user)
    return render(request, template, {'form': form})


@login_required
def update_examination(request, pk):
    """
    Представление для обновления существующей проверки. Загружает текущую
    запись проверки, обрабатывает форму обновления и сохраняет изменения.
    Перенаправляет пользователя на страницу со списком проверок после
    сохранения.

    Параметры:
        - request: Объект запроса, содержащий данные формы.
        - pk: Первичный ключ проверки, которую нужно обновить.

    Возвращает:
        - render: Отображает форму для обновления проверки или перенаправляет
                  на страницу со списком проверок после успешного сохранения.
    """
    examination = get_object_or_404(Examination, pk=pk)
    template = 'facility/examination_update_form.html'
    if request.method == 'POST':
        form = ExaminationUpdateForm(request.POST, instance=examination)
        if form.is_valid():
            form.save()
            cache.delete('examinations_*')
            return redirect('facility:index')
    else:
        form = ExaminationUpdateForm(instance=examination)
    return render(request, template, {'form': form})


@login_required
def delete_examination(request, pk):
    """
    Представление для удаления проверки. Получает объект проверки по
    указанному первичному ключу, подтверждает удаление и удаляет запись
    из базы данных, перенаправляя пользователя на страницу со списком
    проверок.

    Параметры:
        - request: Объект запроса, содержащий данные формы.
        - pk: Первичный ключ проверки, которую нужно удалить.

    Возвращает:
        - render: Отображает страницу подтверждения удаления или
            перенаправляет на страницу со списком проверок после
            успешного удаления.
    """
    examination = get_object_or_404(Examination, pk=pk)
    template = 'facility/examination_confirm_delete.html'
    if request.method == 'POST':
        examination.delete()
        cache.delete('examinations_*')
        return redirect('facility:index')
    return render(request, template, {'examination': examination})
