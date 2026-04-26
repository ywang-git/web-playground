from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from .models import Entity, Event, EventParticipant


def _entity_node(entity):
    return {
        "id": f"entity-{entity.pk}",
        "type": "entity",
        "entity_id": entity.pk,
        "name": entity.name,
        "slug": entity.slug,
        "kind": entity.kind,
    }


def _event_node(event):
    return {
        "id": f"event-{event.pk}",
        "type": "event",
        "event_id": event.pk,
        "title": event.title,
        "when_text": event.when_text,
        "when_sort_key": list(event.when_sort_key),
        "significance": event.significance,
    }


def _source_block(event):
    return {
        "kind": event.source_kind,
        "url": event.source_url,
        "citation": event.source_citation,
        "snippet": event.source_snippet,
    }


def _event_summary(event):
    return {
        "id": event.pk,
        "title": event.title,
        "when_text": event.when_text,
        "when_year": event.when_year,
        "when_sort_key": list(event.when_sort_key),
        "significance": event.significance,
        "source": _source_block(event),
    }


def _event_detail(event):
    place = event.place
    return {
        "id": event.pk,
        "title": event.title,
        "description": event.description,
        "when_text": event.when_text,
        "when_sort_key": list(event.when_sort_key),
        "why": event.why,
        "significance": event.significance,
        "place": (
            {"id": place.pk, "name": place.name, "slug": place.slug}
            if place else None
        ),
        "participants": [
            {
                "id": p.pk,
                "name": p.name,
                "slug": p.slug,
                "kind": p.kind,
            }
            for p in event.participants.all()
        ],
        "source": _source_block(event),
    }


def home(request):
    return render(request, "core/home.html")


def entity_detail(request, slug):
    entity = get_object_or_404(Entity, slug=slug)
    return render(request, "core/entity_detail.html", {"entity": entity})


def api_graph(request):
    entities = list(Entity.objects.all())
    events = list(Event.objects.all().select_related("place"))

    nodes = [_entity_node(e) for e in entities] + [_event_node(ev) for ev in events]

    edges = []
    for ep in EventParticipant.objects.all().select_related("event", "entity"):
        edges.append({
            "source": f"event-{ep.event_id}",
            "target": f"entity-{ep.entity_id}",
            "kind": "participant",
        })
    for ev in events:
        if ev.place_id:
            edges.append({
                "source": f"event-{ev.pk}",
                "target": f"entity-{ev.place_id}",
                "kind": "place",
            })

    return JsonResponse({"nodes": nodes, "edges": edges})


def api_events(request):
    events = Event.objects.all()
    return JsonResponse({"events": [_event_summary(e) for e in events]})


def api_event_detail(request, pk):
    event = get_object_or_404(
        Event.objects.select_related("place").prefetch_related("participants"),
        pk=pk,
    )
    return JsonResponse(_event_detail(event))


def api_entity_detail(request, slug):
    entity = get_object_or_404(Entity, slug=slug)

    seen = {}
    for ev in entity.events.all().select_related("place").prefetch_related("participants"):
        seen[ev.pk] = ev
    for ev in entity.events_here.all().select_related("place").prefetch_related("participants"):
        seen.setdefault(ev.pk, ev)

    events = sorted(seen.values(), key=lambda e: e.when_sort_key)

    # One-hop neighbour graph: entity at center + its events + co-participants/places
    neighbour_entities = {entity.pk: entity}
    for ev in events:
        for p in ev.participants.all():
            neighbour_entities.setdefault(p.pk, p)
        if ev.place_id:
            neighbour_entities.setdefault(ev.place_id, ev.place)

    nodes = [_entity_node(e) for e in neighbour_entities.values()]
    nodes += [_event_node(ev) for ev in events]

    edges = []
    event_ids = {ev.pk for ev in events}
    for ep in EventParticipant.objects.filter(event_id__in=event_ids).select_related("entity"):
        edges.append({
            "source": f"event-{ep.event_id}",
            "target": f"entity-{ep.entity_id}",
            "kind": "participant",
        })
    for ev in events:
        if ev.place_id:
            edges.append({
                "source": f"event-{ev.pk}",
                "target": f"entity-{ev.place_id}",
                "kind": "place",
            })

    return JsonResponse({
        "entity": {
            "id": entity.pk,
            "name": entity.name,
            "slug": entity.slug,
            "kind": entity.kind,
            "description": entity.description,
            "wikipedia_url": entity.wikipedia_url,
        },
        "events": [_event_detail(ev) for ev in events],
        "graph": {"nodes": nodes, "edges": edges},
    })
