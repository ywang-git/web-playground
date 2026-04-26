from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Entity(models.Model):
    PERSON = "PERSON"
    GROUP = "GROUP"
    PLACE = "PLACE"
    ORGANIZATION = "ORGANIZATION"
    OTHER = "OTHER"
    KIND_CHOICES = [
        (PERSON, "Person"),
        (GROUP, "Group"),
        (PLACE, "Place"),
        (ORGANIZATION, "Organization"),
        (OTHER, "Other"),
    ]

    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, default=OTHER)
    description = models.TextField(blank=True)
    wikipedia_url = models.URLField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name) or "entity"
            slug = base
            n = 2
            while Entity.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("entity_detail", args=[self.slug])


class Event(models.Model):
    MAJOR = "MAJOR"
    NORMAL = "NORMAL"
    MINOR = "MINOR"
    SIGNIFICANCE_CHOICES = [
        (MAJOR, "Major"),
        (NORMAL, "Normal"),
        (MINOR, "Minor"),
    ]

    WIKIPEDIA = "WIKIPEDIA"
    WEB = "WEB"
    BOOK = "BOOK"
    NOTE = "NOTE"
    OTHER = "OTHER"
    SOURCE_KIND_CHOICES = [
        (WIKIPEDIA, "Wikipedia"),
        (WEB, "Web"),
        (BOOK, "Book"),
        (NOTE, "Note"),
        (OTHER, "Other"),
    ]
    URL_SOURCE_KINDS = {WIKIPEDIA, WEB}
    CITATION_SOURCE_KINDS = {BOOK, NOTE}

    title = models.CharField(max_length=200)
    description = models.TextField()

    when_year = models.PositiveSmallIntegerField()
    when_month = models.PositiveSmallIntegerField(null=True, blank=True)
    when_day = models.PositiveSmallIntegerField(null=True, blank=True)
    when_end_year = models.PositiveSmallIntegerField(null=True, blank=True)
    when_end_month = models.PositiveSmallIntegerField(null=True, blank=True)
    when_end_day = models.PositiveSmallIntegerField(null=True, blank=True)
    when_text = models.CharField(max_length=120)

    why = models.TextField(blank=True)

    place = models.ForeignKey(
        Entity,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="events_here",
    )

    significance = models.CharField(
        max_length=10, choices=SIGNIFICANCE_CHOICES, default=NORMAL
    )

    source_kind = models.CharField(
        max_length=20, choices=SOURCE_KIND_CHOICES, default=WIKIPEDIA
    )
    source_url = models.URLField(blank=True)
    source_citation = models.CharField(max_length=300, blank=True)
    source_snippet = models.TextField()

    participants = models.ManyToManyField(
        Entity, through="EventParticipant", related_name="events"
    )

    class Meta:
        ordering = ["when_year", "when_month", "when_day"]
        constraints = [
            models.UniqueConstraint(
                fields=["title", "when_year"], name="event_title_year_unique"
            ),
        ]

    def __str__(self):
        return f"{self.title} ({self.when_text})"

    @property
    def when_sort_key(self):
        return (self.when_year, self.when_month or 0, self.when_day or 0)

    def clean(self):
        super().clean()
        if self.place_id and self.place.kind != Entity.PLACE:
            raise ValidationError(
                {"place": "Event.place must reference an Entity with kind=PLACE."}
            )
        if self.source_kind in self.URL_SOURCE_KINDS and not self.source_url:
            raise ValidationError(
                {"source_url": f"source_url is required when source_kind={self.source_kind}."}
            )
        if self.source_kind in self.CITATION_SOURCE_KINDS and not self.source_citation:
            raise ValidationError(
                {"source_citation": f"source_citation is required when source_kind={self.source_kind}."}
            )


class EventParticipant(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("event", "entity")

    def __str__(self):
        return f"{self.entity} in {self.event}"
