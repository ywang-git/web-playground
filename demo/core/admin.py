from django.contrib import admin

from .models import Entity, Event, EventParticipant


class EventParticipantInline(admin.TabularInline):
    model = EventParticipant
    extra = 1
    autocomplete_fields = ["entity"]


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "slug")
    list_filter = ("kind",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "when_text", "significance", "source_kind", "place")
    list_filter = ("significance", "source_kind", "when_year")
    search_fields = ("title", "description", "source_snippet")
    autocomplete_fields = ["place"]
    inlines = [EventParticipantInline]


@admin.register(EventParticipant)
class EventParticipantAdmin(admin.ModelAdmin):
    list_display = ("event", "entity")
    autocomplete_fields = ["event", "entity"]
