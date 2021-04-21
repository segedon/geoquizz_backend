from django.contrib.gis import admin
from .models import Point, Category


admin.site.register(Point, admin.OSMGeoAdmin)
admin.site.register(Category, admin.ModelAdmin)
