from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from datetime import datetime, timedelta
import tempfile
import shutil

from tom_education.utils import timelapse_overseer
from tom_education.models import TimeLapse

class Command(BaseCommand):
    help = 'Update pending blocks if observation requests have been made'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tl_id',
            help='Update timelapse with this ID'
        )

    def handle(self, *args, **options):
        target = None
        if options['tl_id']:
            try:
                tls = TimeLapse.objects.filter(target__pk=options['tl_id'])
            except ObjectDoesNotExist:
                raise Exception('Invalid target id provided')
        else:
            tls = TimeLapse.objects.all()
        for tl in tls:
            self.stdout.write("==== Updating {} timelapse  ====".format(tl.target.id))
            tmpdir = tempfile.mkdtemp()
            timelapse_overseer(tl.id, dir=tmpdir)
            shutil.rmtree(tmpdir)
        if not tls:
            self.stderr.write("No TimeLapse objects available")
