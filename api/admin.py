from django.contrib import admin
from .models import Course, SiteVisit, LinkClick 


class CourseAdmin(admin.ModelAdmin):
    change_list_template = 'admin/courses/courses_change_list.html'



admin.site.register(Course, CourseAdmin)
admin.site.register(SiteVisit)
admin.site.register(LinkClick)
admin.site.site_header = 'Transport and Resources Digital Engineering Streams: Admin Dashboard'