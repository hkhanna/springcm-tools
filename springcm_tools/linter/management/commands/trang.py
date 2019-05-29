import os

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        code = os.system("trang springcm_tools/linter/tags.rnc springcm_tools/linter/tags.rng")        
        if not code:
            self.stdout.write(self.style.SUCCESS('tags.rnc -> tags.rng'))
        else:
            self.stdout.write(self.style.ERROR('Error'))