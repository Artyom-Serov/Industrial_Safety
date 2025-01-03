"""
Модуль представлений, управляющих проверками, аттестуемыми и комиссиями.
"""

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import ExaminationCreateForm, ExaminationUpdateForm
from .models import Examination


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
    paginate_by = settings.DISPLAY_COUNT

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
            filters = {
                'current_check_date': self.request.GET.get(
                    'current_check_date'
                ),
                'next_check_date': self.request.GET.get('next_check_date'),
                'course__course_number__icontains': self.request.GET.get(
                    'course_number'
                ),
                'course__course_name__icontains': self.request.GET.get(
                    'course_name'
                ),
                'examined__brigade__icontains': self.request.GET.get(
                    'brigade'
                ),
            }
            filters = {key: value for key, value in filters.items() if value}
            queryset = queryset.filter(**filters)
            order_by = self.request.GET.get('order_by', '-created_at')
            queryset = queryset.order_by(order_by)
            cache.set(cache_key, queryset, timeout=settings.CACHE_TTL)

        return queryset


class ExaminationCreateView(LoginRequiredMixin, CreateView):
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
    model = Examination
    form_class = ExaminationCreateForm
    template_name = 'facility/examination_create_form.html'
    success_url = reverse_lazy('facility:index')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        cache.delete('examinations_*')
        return response


class ExaminationUpdateView(LoginRequiredMixin,
                            UserPassesTestMixin,
                            UpdateView):
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
    model = Examination
    form_class = ExaminationUpdateForm
    template_name = 'facility/examination_update_form.html'
    success_url = reverse_lazy('facility:index')

    def test_func(self):
        """Проверяет, что пользователь является администратором или
        создателем записи."""
        obj = self.get_object()
        return (self.request.user.is_superuser or obj.examined.user ==
                self.request.user)

    def handle_no_permission(self):
        """Если доступ запрещён, перенаправляем на кастомную страницу 403."""
        raise PermissionDenied

    def form_valid(self, form):
        response = super().form_valid(form)
        cache.delete('examinations_*')
        return response


class ExaminationDeleteView(LoginRequiredMixin,
                            UserPassesTestMixin, DeleteView):
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
    model = Examination
    template_name = 'facility/examination_confirm_delete.html'
    success_url = reverse_lazy('facility:index')

    def test_func(self):
        """Проверяет, что пользователь является администратором или
        создателем записи."""
        obj = self.get_object()
        return (self.request.user.is_superuser or obj.examined.user ==
                self.request.user)

    def handle_no_permission(self):
        """Если доступ запрещён, перенаправляем на кастомную страницу 403."""
        raise PermissionDenied

    def form_valid(self, form):
        response = super().form_valid(form)
        cache.delete('examinations_*')
        return response
