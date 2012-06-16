from json import dumps, loads
import urllib
from xml.etree import ElementTree
from census.core import Census
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
import os
import redis

redis_conn = redis.from_url(os.getenv('REDISTOGO_URL', 'redis://localhost:6379'))
try:
    census_api_key = os.getenv("CENSUS_API_KEY", settings.CENSUS_API_KEY)
except NameError:
    raise Exception("CENSUS_API_KEY setting is not defined!")
census_api_client = Census(census_api_client)

api_schema_str = urllib.urlopen("http://www.census.gov/developers/data/2010acs5_variables.xml").read()
api_schema = ElementTree.fromstring(api_schema_str)

api_params = {}
for concept_elem in api_schema.findall("concept"):
    concept_name = concept_elem.attrib['name'].split(". ")[-1].strip()
    api_params[concept_name] = {}
    for index, variable in enumerate(concept_elem.findall("variable")):
        api_params[concept_name][variable.attrib["name"]] = (index, variable.text)


def cached_call(key, method, *args, **kwargs):
    res = redis_conn.get(key)
    if res is not None:
        return loads(res)
    res = method(*args, **kwargs)
    redis_conn.set(key, dumps(res))
    return res


def index(request):
    states = cached_call("states", census_api_client.acs.state, ("NAME",), "*")
    counties = cached_call("counties", census_api_client.acs.state_county, ("NAME",), "*", "*")
    state_names = {}
    for state_data in states:
        state_names[state_data['state']] = state_data['NAME']
    for i in range(len(counties)):
        counties[i]["STATE_NAME"] = state_names[counties[i]["state"]]
    return render_to_response("index.html", RequestContext(request, {"counties": counties}))

def get_statistics(request):
    return HttpResponse(dumps(api_params.keys()))

def get_statistics_for_county(request, state_county, statistic_type):
    # CENSUS API allows to pass maximum 5 statitics in request.
    # Therefore we have to make several successive requests to get all statistics from the group
    redis_cache_key = ",".join([state_county, statistic_type])
    cache_res = redis_conn.get(redis_cache_key)
    if cache_res is not None:
        return HttpResponse(cache_res)
    state_id, county_id = state_county.split(",")
    res = []
    for i in range(0, len(api_params[statistic_type].keys()), 5):
        j = min(len(api_params[statistic_type].keys()), i+5)
        part_res = census_api_client.acs.state_county(
            tuple(api_params[statistic_type].keys()[i:j]),
            state_id,
            county_id
        )[0]
        for key, value in part_res.items():
            if key in ("county", "state"):
                continue
            res.append([api_params[statistic_type][key][0], api_params[statistic_type][key][1], value])
    res = dumps(sorted(res, key=lambda elem: elem[0]))
    redis_conn.set(redis_cache_key, res)
    return HttpResponse(res)