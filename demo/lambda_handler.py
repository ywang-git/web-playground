import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "demo.settings")

import django

django.setup()

from mangum import Mangum

from demo.asgi import application

handler = Mangum(application, lifespan="off")


def migrate(event, context):
    from django.core.management import call_command

    call_command("migrate", interactive=False)
    return {"ok": True}
