from django.contrib import admin
from .models import Correction, CorrectionItem

# Register your models here.
admin.site.register(Correction)
admin.site.register(CorrectionItem)