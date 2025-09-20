from django.contrib import admin
from .models import TerratracUser, Badge, ForestArea, NDVIRecord, Alert, CommunityReport, Verification

# Register your models here.
admin.site.register(TerratracUser)
admin.site.register(Badge)
admin.site.register(ForestArea)
admin.site.register(NDVIRecord)
admin.site.register(Alert)
admin.site.register(CommunityReport)
admin.site.register(Verification)