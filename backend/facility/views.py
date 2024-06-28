from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Examination, Examined, Commission, Briefing, Course
from .forms import ExaminationForm


class IndexView(ListView):
    model = Examination
    template_name = 'facility/index.html'
    context_object_name = 'examinations'
    ordering = ['-created_at']

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Examination.objects.filter(
                examined__company_name=self.request.user.organization
            ).order_by('-created_at')
        return Examination.objects.none()


@login_required
def create_examination(request):
    template = 'facility/examination_form.html'
    if request.method == 'POST':
        form = ExaminationForm(request.POST)
        if form.is_valid():
            examination = form.save(commit=False)
            examination.save()
            return redirect('facility:index')
    else:
        form = ExaminationForm()
    return render(request, template, {'form': form})


@login_required
def update_examination(request, pk):
    examination = get_object_or_404(Examination, pk=pk)
    template = 'facility/examination_form.html'
    if request.method == 'POST':
        form = ExaminationForm(request.POST, instance=examination)
        if form.is_valid():
            form.save()
            return redirect('facility:index')
    else:
        form = ExaminationForm(instance=examination)
    return render(request, template, {'form': form})


@login_required
def delete_examination(request, pk):
    examination = get_object_or_404(Examination, pk=pk)
    template = 'facility/examination_confirm_delete.html'
    if request.method == 'POST':
        examination.delete()
        return redirect('facility:index')
    return render(request, template, {'examination': examination})
