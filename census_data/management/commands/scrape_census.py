from django.core.management.base import BaseCommand, CommandError
import os
import redis
from json import loads
from census_data.views import get_statistics_for_area

class Command(BaseCommand):
    help = 'Scrapes census API and put data to Redis cache'
    def handle(self, *args, **options):
        redis_conn = redis.from_url(os.getenv('REDISTOGO_URL', 'redis://localhost:6379'))
        states = redis_conn.get("states")
        if states is None:
            raise CommandError('"states" are not in redis cache!')
        states = loads(states)

        for state_data in states:
            self.stdout.write("Processing state: %s\n" %state_data["NAME"])
            get_statistics_for_area(None, state_data["state"])

        counties= redis_conn.get("counties")
        if counties is None:
            raise CommandError('"counties" are not in redis cache!')
        counties = loads(counties)

        for county_data in counties:
            self.stdout.write("Processing county: %s\n" %county_data["NAME"])
            get_statistics_for_area(None, "%s,%s" %(county_data["state"], county_data["county"]))

        for state_data in states:
            state_msas = redis_conn.get("msa,%s" %state_data['state'])
            if state_msas is None:
                raise CommandError('"counties" are not in redis cache!')
            state_msas = loads(state_msas)
            for msa_data in state_msas:
                self.stdout.write("Processing msa: %s\n" %msa_data["NAME"])
                get_statistics_for_area(None, "%s,%s," %(msa_data["state"], msa_data["metropolitan statistical area/micropolitan statistical area"]))