from django.contrib.gis import admin
from .models import Point, Category, Game, Round


admin.site.register(Point, admin.OSMGeoAdmin)
admin.site.register(Category, admin.ModelAdmin)
admin.site.register(Game, admin.ModelAdmin)
admin.site.register(Round, admin.OSMGeoAdmin)
