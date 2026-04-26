from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("entity/<slug:slug>/", views.entity_detail, name="entity_detail"),
    path("api/graph/", views.api_graph, name="api_graph"),
    path("api/events/", views.api_events, name="api_events"),
    path("api/events/<int:pk>/", views.api_event_detail, name="api_event_detail"),
    path("api/entity/<slug:slug>/", views.api_entity_detail, name="api_entity_detail"),
]
