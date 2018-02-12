"""
Django management command to create a course in a specific modulestore
"""
from six import text_type
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from contentstore.management.commands.utils import user_from_str
from contentstore.views.course import create_new_course_in_store
from xmodule.modulestore import ModuleStoreEnum


MODULESTORE_CHOICES = (ModuleStoreEnum.Type.mongo, ModuleStoreEnum.Type.split)


class Command(BaseCommand):
    """
    Create a course in a specific modulestore.
    """

    # can this query modulestore for the list of write accessible stores or does that violate command pattern?
    help = "Create a course in one of {}".format([ModuleStoreEnum.Type.mongo, ModuleStoreEnum.Type.split])

    def add_arguments(self, parser):
        parser.add_argument('modulestore',
                            choices=MODULESTORE_CHOICES,
                            help="Modulestore must be one of {}".format(MODULESTORE_CHOICES))
        parser.add_argument('user',
                            help="The instructor's email address or integer ID.")
        parser.add_argument('org',
                            help="The organization to create the course within.")
        parser.add_argument('number',
                            help="The number of the course.")
        parser.add_argument('run',
                            help="The name of the course run.")
        parser.add_argument('name',
                            nargs='?',
                            default=None,
                            help="The display name of the course. (OPTIONAL)")
        parser.add_argument('start_date',
                            nargs='?',
                            default=None,
                            help="The start date of the course. Format: YYYY-MM-DD")

    def parse_args(self, **options):
        """
        Return a tuple of passed in values for (modulestore, user, org, number, run, name, start_date).
        """
        try:
            user = user_from_str(options['user'])
        except User.DoesNotExist:
            raise CommandError("No user {user} found.".format(user=options['user']))

        return options['modulestore'], user, options['org'], options['number'], options['run'], options['name'], \
               options["start_date"]

    def handle(self, *args, **options):
        storetype, user, org, number, run, name, start_date = self.parse_args(**options)

        # start date is set one week ago if not given
        start_date = datetime.strptime(start_date, "%Y-%m-%d") if start_date else datetime.now() - timedelta(days=7)

        if storetype == ModuleStoreEnum.Type.mongo:
            self.stderr.write("WARNING: The 'Old Mongo' store is deprecated. New courses should be added to split.")

        fields = {
            "start": start_date
        }
        if name:
            fields["display_name"] = name
        new_course = create_new_course_in_store(
            storetype,
            user,
            org,
            number,
            run,
            fields
        )
        self.stdout.write(u"Created {}".format(text_type(new_course.id)))
