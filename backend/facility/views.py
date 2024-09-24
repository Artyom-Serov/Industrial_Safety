from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from .models import Examination
from .forms import ExaminationCreateForm, ExaminationUpdateForm


class IndexView(ListView):
    model = Examination
    template_name = 'facility/index.html'
    context_object_name = 'examinations'
    ordering = ['-created_at']

    def get_queryset(self):
        if self.request.user.is_authenticated:
            if self.request.user.is_superuser:
                queryset = Examination.objects.all()
            else:
                queryset = Examination.objects.filter(
                    examined__company_name=self.request.user.organization
                )

            current_check_date = self.request.GET.get('current_check_date')
            next_check_date = self.request.GET.get('next_check_date')
            course_number = self.request.GET.get('course_number')
            course_name = self.request.GET.get('course_name')
            brigade = self.request.GET.get('brigade')
            order_by = self.request.GET.get('order_by', '-created_at')

            if current_check_date:
                queryset = queryset.filter(current_check_date=current_check_date)
            if next_check_date:
                queryset = queryset.filter(next_check_date=next_check_date)
            if course_number:
                queryset = queryset.filter(course__course_number__icontains=course_number)
            if course_name:
                queryset = queryset.filter(course__course_name__icontains=course_name)
            if brigade:
                queryset = queryset.filter(examined__brigade__icontains=brigade)
            queryset = queryset.order_by(order_by)

            return queryset
        return Examination.objects.none()


@login_required
def create_examination(request):
    template = 'facility/examination_create_form.html'
    if request.method == 'POST':
        form = ExaminationCreateForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('facility:index')
    else:
        form = ExaminationCreateForm(user=request.user)
    return render(request, template, {'form': form})


@login_required
def update_examination(request, pk):
    examination = get_object_or_404(Examination, pk=pk)
    template = 'facility/examination_update_form.html'
    if request.method == 'POST':
        form = ExaminationUpdateForm(request.POST, instance=examination)
        if form.is_valid():
            form.save()
            return redirect('facility:index')
    else:
        form = ExaminationUpdateForm(instance=examination)
    return render(request, template, {'form': form})


@login_required
def delete_examination(request, pk):
    examination = get_object_or_404(Examination, pk=pk)
    template = 'facility/examination_confirm_delete.html'
    if request.method == 'POST':
        examination.delete()
        return redirect('facility:index')
    return render(request, template, {'examination': examination})
