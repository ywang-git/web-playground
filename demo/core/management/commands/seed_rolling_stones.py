from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import Entity, Event, EventParticipant

ENTITIES = [
    # Groups
    ("The Rolling Stones", Entity.GROUP, "English rock band formed in London in 1962.",
     "https://en.wikipedia.org/wiki/The_Rolling_Stones"),
    ("The Beatles", Entity.GROUP, "English rock band formed in Liverpool in 1960.",
     "https://en.wikipedia.org/wiki/The_Beatles"),
    ("The Spiders from Mars", Entity.GROUP,
     "David Bowie's backing band during the Ziggy Stardust era.",
     "https://en.wikipedia.org/wiki/The_Spiders_from_Mars"),

    # People — Stones
    ("Mick Jagger", Entity.PERSON, "Lead vocalist and co-principal songwriter of The Rolling Stones.",
     "https://en.wikipedia.org/wiki/Mick_Jagger"),
    ("Keith Richards", Entity.PERSON, "Guitarist and co-principal songwriter of The Rolling Stones.",
     "https://en.wikipedia.org/wiki/Keith_Richards"),
    ("Brian Jones", Entity.PERSON, "Founding member and multi-instrumentalist of The Rolling Stones.",
     "https://en.wikipedia.org/wiki/Brian_Jones"),
    ("Charlie Watts", Entity.PERSON, "Drummer of The Rolling Stones from 1963 until his death in 2021.",
     "https://en.wikipedia.org/wiki/Charlie_Watts"),
    ("Bill Wyman", Entity.PERSON, "Bassist of The Rolling Stones from 1962 to 1993.",
     "https://en.wikipedia.org/wiki/Bill_Wyman"),
    ("Ronnie Wood", Entity.PERSON, "Guitarist; joined The Rolling Stones in 1975.",
     "https://en.wikipedia.org/wiki/Ronnie_Wood"),
    ("Mick Taylor", Entity.PERSON,
     "Guitarist; replaced Brian Jones in The Rolling Stones from 1969 to 1974.",
     "https://en.wikipedia.org/wiki/Mick_Taylor"),
    ("Andrew Loog Oldham", Entity.PERSON,
     "Manager and producer who shaped the early Rolling Stones image.",
     "https://en.wikipedia.org/wiki/Andrew_Loog_Oldham"),

    # People — Bowie circle
    ("David Bowie", Entity.PERSON,
     "English singer-songwriter, key figure in popular music for over five decades.",
     "https://en.wikipedia.org/wiki/David_Bowie"),
    ("Mick Ronson", Entity.PERSON,
     "Guitarist and producer best known for his work with David Bowie.",
     "https://en.wikipedia.org/wiki/Mick_Ronson"),

    # Places
    ("London", Entity.PLACE, "Capital of England and the United Kingdom.",
     "https://en.wikipedia.org/wiki/London"),
    ("Marquee Club", Entity.PLACE,
     "Historic London music venue; site of the first Rolling Stones gig.",
     "https://en.wikipedia.org/wiki/Marquee_Club"),
    ("Wembley Stadium", Entity.PLACE,
     "Stadium in London; venue of the 1985 Live Aid concert.",
     "https://en.wikipedia.org/wiki/Wembley_Stadium_(1923)"),
    ("Altamont Speedway", Entity.PLACE,
     "Former racetrack in California; site of the 1969 Altamont Free Concert.",
     "https://en.wikipedia.org/wiki/Altamont_Speedway"),
    ("Hyde Park, London", Entity.PLACE, "Royal park in central London.",
     "https://en.wikipedia.org/wiki/Hyde_Park,_London"),
    ("Hammersmith Odeon", Entity.PLACE,
     "London concert hall where Bowie 'retired' Ziggy Stardust in 1973.",
     "https://en.wikipedia.org/wiki/Hammersmith_Apollo"),
]


def _w(url, snippet):
    return {
        "source_kind": Event.WIKIPEDIA,
        "source_url": url,
        "source_citation": "",
        "source_snippet": snippet,
    }


def _book(citation, snippet):
    return {
        "source_kind": Event.BOOK,
        "source_url": "",
        "source_citation": citation,
        "source_snippet": snippet,
    }


def _note(citation, snippet):
    return {
        "source_kind": Event.NOTE,
        "source_url": "",
        "source_citation": citation,
        "source_snippet": snippet,
    }


EVENTS = [
    {
        "title": "First Rolling Stones gig at the Marquee Club",
        "description": "Brian Jones, Mick Jagger and Keith Richards perform under "
                       "the name 'The Rollin' Stones' at London's Marquee Club.",
        "when_year": 1962, "when_month": 7, "when_day": 12,
        "when_text": "12 July 1962",
        "why": "Brian Jones placed an ad recruiting musicians for an R&B band; "
               "this date is conventionally treated as the band's debut.",
        "place": "Marquee Club",
        "significance": Event.MAJOR,
        "participants": ["Brian Jones", "Mick Jagger", "Keith Richards", "The Rolling Stones"],
        **_w(
            "https://en.wikipedia.org/wiki/The_Rolling_Stones",
            "The Rolling Stones played their first gig at the Marquee Club in "
            "London on 12 July 1962, billed as 'The Rollin' Stones'.",
        ),
    },
    {
        "title": "Charlie Watts joins The Rolling Stones",
        "description": "Drummer Charlie Watts leaves Blues Incorporated and "
                       "becomes the permanent drummer of The Rolling Stones.",
        "when_year": 1963, "when_month": 1,
        "when_text": "January 1963",
        "why": "The band needed a steady drummer; Watts had been gigging with them informally.",
        "place": "London",
        "significance": Event.MAJOR,
        "participants": ["Charlie Watts", "The Rolling Stones"],
        **_w(
            "https://en.wikipedia.org/wiki/Charlie_Watts",
            "Watts joined the Rolling Stones in January 1963 and remained their "
            "drummer until his death in 2021.",
        ),
    },
    {
        "title": "Andrew Loog Oldham becomes Stones manager",
        "description": "19-year-old Andrew Loog Oldham signs on as the band's "
                       "manager and reshapes their public image as the anti-Beatles.",
        "when_year": 1963, "when_month": 5,
        "when_text": "May 1963",
        "why": "Oldham saw a marketing opening opposite the Beatles' clean-cut image.",
        "place": "London",
        "significance": Event.NORMAL,
        "participants": ["Andrew Loog Oldham", "The Rolling Stones", "The Beatles"],
        **_w(
            "https://en.wikipedia.org/wiki/Andrew_Loog_Oldham",
            "Oldham became the Stones' manager in May 1963 and is credited with "
            "shaping their image as the anti-Beatles.",
        ),
    },
    {
        "title": "Bill Wyman replaces Dick Taylor on bass",
        "description": "Bill Wyman becomes the bassist of The Rolling Stones.",
        "when_year": 1962, "when_month": 12,
        "when_text": "December 1962",
        "why": "The band needed a permanent bassist with his own equipment.",
        "place": "London",
        "significance": Event.MINOR,
        "participants": ["Bill Wyman", "The Rolling Stones"],
        **_w(
            "https://en.wikipedia.org/wiki/Bill_Wyman",
            "Wyman auditioned in December 1962 and stayed with the band for over "
            "30 years.",
        ),
    },
    {
        "title": "Brian Jones leaves The Rolling Stones",
        "description": "Brian Jones is dismissed from the band he founded; "
                       "Mick Taylor is announced as his replacement.",
        "when_year": 1969, "when_month": 6, "when_day": 8,
        "when_text": "8 June 1969",
        "why": "Jones's drug problems and creative drift had isolated him from "
               "the band's working core.",
        "place": "London",
        "significance": Event.MAJOR,
        "participants": ["Brian Jones", "Mick Jagger", "Keith Richards", "Mick Taylor",
                          "The Rolling Stones"],
        **_w(
            "https://en.wikipedia.org/wiki/Brian_Jones",
            "On 8 June 1969 Jagger, Richards and Watts visited Jones at his home "
            "and told him the band would continue without him.",
        ),
    },
    {
        "title": "Hyde Park free concert / Brian Jones tribute",
        "description": "Two days after Brian Jones's death, the Stones play a "
                       "free concert in Hyde Park; Mick Jagger reads from Shelley's 'Adonais'.",
        "when_year": 1969, "when_month": 7, "when_day": 5,
        "when_text": "5 July 1969",
        "why": "Originally planned to introduce Mick Taylor; converted into a tribute.",
        "place": "Hyde Park, London",
        "significance": Event.NORMAL,
        "participants": ["Mick Jagger", "Keith Richards", "Mick Taylor", "Charlie Watts",
                          "Bill Wyman", "The Rolling Stones"],
        **_w(
            "https://en.wikipedia.org/wiki/The_Rolling_Stones_in_Hyde_Park",
            "An estimated 250,000 to 500,000 people attended the free concert in "
            "Hyde Park on 5 July 1969.",
        ),
    },
    {
        "title": "Altamont Free Concert",
        "description": "Free festival headlined by The Rolling Stones; marred by "
                       "violence including the killing of Meredith Hunter.",
        "when_year": 1969, "when_month": 12, "when_day": 6,
        "when_text": "6 December 1969",
        "why": "The Stones wanted a US analogue to their Hyde Park free show.",
        "place": "Altamont Speedway",
        "significance": Event.MAJOR,
        "participants": ["Mick Jagger", "Keith Richards", "Mick Taylor", "Charlie Watts",
                          "Bill Wyman", "The Rolling Stones"],
        **_w(
            "https://en.wikipedia.org/wiki/Altamont_Free_Concert",
            "The Altamont Free Concert took place on December 6, 1969, at the "
            "Altamont Speedway in Northern California.",
        ),
    },
    {
        "title": "Mick Taylor leaves the band",
        "description": "Guitarist Mick Taylor unexpectedly resigns from The Rolling Stones.",
        "when_year": 1974, "when_month": 12,
        "when_text": "December 1974",
        "why": "Taylor cited a lack of songwriting credit and the band's lifestyle.",
        "place": "London",
        "significance": Event.NORMAL,
        "participants": ["Mick Taylor", "Mick Jagger", "Keith Richards", "The Rolling Stones"],
        **_w(
            "https://en.wikipedia.org/wiki/Mick_Taylor",
            "Taylor announced his departure in December 1974, surprising the rest "
            "of the band mid-album.",
        ),
    },
    {
        "title": "Ronnie Wood joins The Rolling Stones",
        "description": "Ronnie Wood, formerly of Faces, joins as second guitarist.",
        "when_year": 1975, "when_month": 4,
        "when_text": "April 1975",
        "why": "The band needed a guitarist for the upcoming Tour of the Americas.",
        "place": "London",
        "significance": Event.MAJOR,
        "participants": ["Ronnie Wood", "Mick Jagger", "Keith Richards", "The Rolling Stones"],
        **_w(
            "https://en.wikipedia.org/wiki/Ronnie_Wood",
            "Wood toured with the Stones in 1975 and officially joined the band "
            "as a full member in 1976.",
        ),
    },
    {
        "title": "Release of 'The Rise and Fall of Ziggy Stardust and the Spiders from Mars'",
        "description": "David Bowie releases the concept album that introduces "
                       "the Ziggy Stardust persona.",
        "when_year": 1972, "when_month": 6, "when_day": 16,
        "when_text": "16 June 1972",
        "why": "Bowie sought a rock-theatre vehicle to break through commercially.",
        "place": "London",
        "significance": Event.MAJOR,
        "participants": ["David Bowie", "Mick Ronson", "The Spiders from Mars"],
        **_w(
            "https://en.wikipedia.org/wiki/The_Rise_and_Fall_of_Ziggy_Stardust_and_the_Spiders_from_Mars",
            "The album was released on 16 June 1972 and is widely regarded as a "
            "landmark of glam rock.",
        ),
    },
    {
        "title": "'Retirement' of Ziggy Stardust at the Hammersmith Odeon",
        "description": "Bowie shocks his band by announcing on stage that 'this "
                       "is the last show we'll ever do'.",
        "when_year": 1973, "when_month": 7, "when_day": 3,
        "when_text": "3 July 1973",
        "why": "Bowie wanted to retire the Ziggy persona before it consumed him.",
        "place": "Hammersmith Odeon",
        "significance": Event.MAJOR,
        "participants": ["David Bowie", "Mick Ronson", "The Spiders from Mars"],
        **_w(
            "https://en.wikipedia.org/wiki/Ziggy_Stardust_Tour",
            "On 3 July 1973 Bowie announced from the Hammersmith stage that the "
            "show would be 'the last show that we'll ever do'.",
        ),
    },
    {
        "title": "Jagger and Bowie record 'Dancing in the Street' for Live Aid",
        "description": "Mick Jagger and David Bowie record a cover of Martha and "
                       "the Vandellas' 'Dancing in the Street' to benefit Live Aid.",
        "when_year": 1985, "when_month": 6,
        "when_text": "June 1985",
        "why": "A planned trans-Atlantic satellite duet at Live Aid was deemed "
               "technically impossible, so they recorded a single instead.",
        "place": "London",
        "significance": Event.MAJOR,
        "participants": ["Mick Jagger", "David Bowie", "The Rolling Stones"],
        **_w(
            "https://en.wikipedia.org/wiki/Dancing_in_the_Street",
            "Jagger and Bowie recorded the cover and accompanying video in late "
            "June 1985 specifically to benefit the Live Aid charity effort.",
        ),
    },
    {
        "title": "Live Aid concert at Wembley Stadium",
        "description": "David Bowie performs at the Live Aid charity concert; "
                       "the Jagger/Bowie 'Dancing in the Street' video premieres globally.",
        "when_year": 1985, "when_month": 7, "when_day": 13,
        "when_text": "13 July 1985",
        "why": "Famine relief in Ethiopia.",
        "place": "Wembley Stadium",
        "significance": Event.MAJOR,
        "participants": ["David Bowie", "Mick Jagger"],
        **_w(
            "https://en.wikipedia.org/wiki/Live_Aid",
            "Live Aid was held on 13 July 1985 at Wembley Stadium in London and "
            "JFK Stadium in Philadelphia.",
        ),
    },
    {
        "title": "Charlie Watts dies",
        "description": "Drummer Charlie Watts dies in London at the age of 80.",
        "when_year": 2021, "when_month": 8, "when_day": 24,
        "when_text": "24 August 2021",
        "why": "Watts had withdrawn from the band's tour earlier in the month for medical reasons.",
        "place": "London",
        "significance": Event.MAJOR,
        "participants": ["Charlie Watts", "The Rolling Stones"],
        **_w(
            "https://en.wikipedia.org/wiki/Charlie_Watts",
            "Watts died in a London hospital on 24 August 2021, surrounded by his family.",
        ),
    },
    {
        "title": "Oldham orchestrates the 'Would you let your sister go with a Rolling Stone?' campaign",
        "description": "Oldham seeds the press with the line that crystallises the "
                       "Stones' bad-boy image versus the Beatles'.",
        "when_year": 1964,
        "when_text": "1964",
        "why": "To brand the Stones in deliberate opposition to The Beatles.",
        "place": "London",
        "significance": Event.NORMAL,
        "participants": ["Andrew Loog Oldham", "The Rolling Stones", "The Beatles"],
        **_book(
            "Philip Norman, 'The Stones', Penguin, 1984, p. 112.",
            "Oldham personally fed the 'Would you let your sister go with a "
            "Rolling Stone?' headline to a tabloid sub-editor over drinks.",
        ),
    },
    {
        "title": "Jagger and Richards meet again at Dartford station",
        "description": "Childhood acquaintances Mick Jagger and Keith Richards "
                       "bump into each other at Dartford railway station; Jagger is "
                       "carrying blues records under his arm.",
        "when_year": 1961, "when_month": 10, "when_day": 17,
        "when_text": "17 October 1961",
        "why": "Chance encounter that triggered their musical partnership.",
        "place": "London",
        "significance": Event.MAJOR,
        "participants": ["Mick Jagger", "Keith Richards"],
        **_book(
            "Keith Richards, 'Life', Little, Brown, 2010, pp. 70-71.",
            "Richards recalls Jagger's stack of imported Chess Records on the "
            "platform at Dartford as the moment that 'reset' their friendship.",
        ),
    },
    {
        "title": "Small unannounced club gig (lineup notes)",
        "description": "Personal-archive note recording an unadvertised early "
                       "Stones rehearsal-show in a Soho basement.",
        "when_year": 1962, "when_month": 9,
        "when_text": "September 1962",
        "why": "Working out new R&B covers in front of a tiny audience.",
        "place": "London",
        "significance": Event.MINOR,
        "participants": ["Brian Jones", "Mick Jagger", "Keith Richards", "The Rolling Stones"],
        **_note(
            "Personal notebook, collector archive (unpublished).",
            "Set list opened with 'Dust My Broom'; estimated audience of 14.",
        ),
    },
    {
        "title": "Bowie meets Mick Ronson",
        "description": "Bowie is introduced to guitarist Mick Ronson, beginning "
                       "the partnership behind Ziggy Stardust.",
        "when_year": 1970, "when_month": 2,
        "when_text": "February 1970",
        "why": "Bowie was assembling a harder-edged backing band.",
        "place": "London",
        "significance": Event.NORMAL,
        "participants": ["David Bowie", "Mick Ronson"],
        **_w(
            "https://en.wikipedia.org/wiki/Mick_Ronson",
            "Bowie met Ronson in early 1970 and immediately recruited him for "
            "what would become 'The Man Who Sold the World'.",
        ),
    },
]


class Command(BaseCommand):
    help = "Seed the database with hand-curated Rolling Stones / Bowie entities and events."

    @transaction.atomic
    def handle(self, *args, **options):
        # Entities first
        entities_by_name = {}
        for name, kind, description, wiki in ENTITIES:
            obj, _ = Entity.objects.update_or_create(
                name=name,
                defaults={
                    "kind": kind,
                    "description": description,
                    "wikipedia_url": wiki,
                },
            )
            entities_by_name[name] = obj

        # Events
        for spec in EVENTS:
            place_name = spec.get("place")
            place_obj = entities_by_name.get(place_name) if place_name else None

            defaults = {
                "description": spec["description"],
                "when_month": spec.get("when_month"),
                "when_day": spec.get("when_day"),
                "when_end_year": spec.get("when_end_year"),
                "when_end_month": spec.get("when_end_month"),
                "when_end_day": spec.get("when_end_day"),
                "when_text": spec["when_text"],
                "why": spec.get("why", ""),
                "place": place_obj,
                "significance": spec.get("significance", Event.NORMAL),
                "source_kind": spec["source_kind"],
                "source_url": spec.get("source_url", ""),
                "source_citation": spec.get("source_citation", ""),
                "source_snippet": spec["source_snippet"],
            }
            event, _ = Event.objects.update_or_create(
                title=spec["title"],
                when_year=spec["when_year"],
                defaults=defaults,
            )

            participant_objs = [entities_by_name[n] for n in spec.get("participants", [])]
            wanted_ids = {e.pk for e in participant_objs}
            current_ids = set(
                EventParticipant.objects.filter(event=event).values_list("entity_id", flat=True)
            )
            for entity in participant_objs:
                if entity.pk not in current_ids:
                    EventParticipant.objects.create(event=event, entity=entity)
            EventParticipant.objects.filter(event=event).exclude(entity_id__in=wanted_ids).delete()

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {Entity.objects.count()} entities, "
            f"{Event.objects.count()} events, "
            f"{EventParticipant.objects.count()} participations."
        ))
