from django.contrib import admin
from clearance.models import *
# Register your models here.
admin.site.register(Student)
admin.site.register(Department)
admin.site.register(ClearanceRequest)
admin.site.register(ClearanceSlip)