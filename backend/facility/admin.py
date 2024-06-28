from django.contrib import admin
from .models import Commission, Examined, Briefing, Course, Examination


class ExaminedAdmin(admin.ModelAdmin):
    list_display = (
        'full_name', 'position', 'brigade',
        'company_name', 'safety_group', 'work_experience'
    )
    list_filter = ('brigade', 'company_name', 'safety_group')


class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_number', 'course_name', 'certificate_number')
    list_filter = ('course_number', 'course_name')


class ExaminationAdmin(admin.ModelAdmin):
    list_display = (
        'created_at', 'current_check_date', 'next_check_date',
        'protocol_number', 'examined', 'commission', 'briefing',
        'course'
    )
    list_filter = ('current_check_date', 'next_check_date')


admin.site.register(Commission)
admin.site.register(Examined, ExaminedAdmin)
admin.site.register(Briefing)
admin.site.register(Course, CourseAdmin)
admin.site.register(Examination, ExaminationAdmin)
