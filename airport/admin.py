from django.contrib import admin

from airport.models import (
    Airport,
    Country,
    City,
    Route,
    Crew,
    Flight,
    AirplaneType,
    Airplane
)

admin.site.register(Country)
admin.site.register(City)
admin.site.register(Airport)
admin.site.register(Flight)
admin.site.register(Route)
admin.site.register(Crew)
admin.site.register(Airplane)
admin.site.register(AirplaneType)
