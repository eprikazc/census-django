from collections import OrderedDict
from json import dumps, loads
import urllib
from xml.etree import ElementTree
from census.core import Census
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from utils import STATE_ABBREVIATIONS, convert_input_value_for_fred_app, wkhtml_pdf
import os
import redis

STATISTICS_OF_INTEREST = (("SF1", "TENURE [4]"), ("SF1", "RACE [8]"), ("SF1", "VACANCY STATUS [8]"),
                          ("SF1", "HOUSEHOLD TYPE [9]"), ("SF1", "Sex By Age [49]"), ("ACS", "Median Household Income"))

redis_conn = redis.from_url(os.getenv('REDISTOGO_URL', 'redis://localhost:6379'))
try:
    census_api_key = os.getenv("CENSUS_API_KEY", settings.CENSUS_API_KEY)
except NameError:
    raise Exception("CENSUS_API_KEY setting is not defined!")
census_api_client = Census(census_api_key)

sf1_api_schema_str = redis_conn.get("sf1_api_schema_str")
if sf1_api_schema_str is None:
    sf1_api_schema_str = urllib.urlopen("http://www.census.gov/developers/data/sf1.xml").read()
    redis_conn.set("sf1_api_schema_str", sf1_api_schema_str)
sf1_api_schema = ElementTree.fromstring(sf1_api_schema_str)

sf1_api_params = {}
for concept_elem in sf1_api_schema.findall("concept"):
    concept_name = concept_elem.attrib['name'].split(". ")[-1].strip()
    sf1_api_params[concept_name] = {}
    for index, variable in enumerate(concept_elem.findall("variable")):
        sf1_api_params[concept_name][variable.attrib["name"]] = (index, variable.text)


acs_api_schema_str = redis_conn.get("acs_api_schema_str")
if acs_api_schema_str is None:
    acs_api_schema_str = urllib.urlopen("http://www.census.gov/developers/data/2010acs5_variables.xml").read()
    redis_conn.set("acs_api_schema_str", acs_api_schema_str)
acs_api_schema = ElementTree.fromstring(acs_api_schema_str)

acs_api_params = {}
for concept_elem in acs_api_schema.findall("concept"):
    concept_name = concept_elem.attrib['name'].split(". ")[-1].strip()
    acs_api_params[concept_name] = {}
    for index, variable in enumerate(concept_elem.findall("variable")):
        acs_api_params[concept_name][variable.attrib["name"]] = (index, variable.text)



def cached_call(key, method, *args, **kwargs):
    res = redis_conn.get(key)
    if res is not None:
        return loads(res)
    res = method(*args, **kwargs)
    redis_conn.set(key, dumps(res))
    return res


def index(request):
    states = cached_call("states", census_api_client.sf1.state, ("NAME",), "*")
    counties_list = cached_call("counties", census_api_client.sf1.state_county, ("NAME",), "*", "*")
    # Census API does not allow to receive all MSAs in one request. Therefore we make request for every state
    msas = OrderedDict()
    counties = OrderedDict()
    state_names = {}
    for state_data in states:
        state_names[state_data['state']] = state_data['NAME']
        msa_res = cached_call(
            "msa,%s" %state_data['state'],
            census_api_client.sf1.state_msa, ("NAME",), state_data['state'], "*"
        )
        for i in range(len(msa_res)):
            msa_res[i]["msa_code"] = msa_res[i]['metropolitan statistical area/micropolitan statistical area']
            msa_res[i]["STATE_ABBREVIATION"] = STATE_ABBREVIATIONS[state_data["NAME"]]
        msas[state_data['NAME']] = msa_res

    for i in range(len(counties_list)):
        state_name = state_names[counties_list[i]["state"]]
        counties_list[i]["STATE_ABBREVIATION"] = STATE_ABBREVIATIONS[state_name]
        counties.setdefault(state_name, []).append(counties_list[i])
    return render_to_response("index.html", RequestContext(
        request, {"counties": counties, "states": states, "msas": msas}
    ))

def get_statistics(request):
    return HttpResponse(dumps(sf1_api_params.keys()))

def get_statistics_for_area(request, area):
    """
    'area' parameter may have following values:
    area=01 - state is 01
    area=01,001 - state is 01, county is 001
    area=01,001, - state is 01, MSA is 001
    """
    # CENSUS API allows to pass maximum 5 statitics in request.
    # Therefore we have to make several successive requests to get all statistics from the group
    res = {}
    split_area = area.split(",")
    if len(split_area) ==1:
        sf1_method = census_api_client.sf1.state
        acs_method = census_api_client.acs.state
        api_method_args = tuple(split_area)
    elif len(split_area) == 2:
        sf1_method = census_api_client.sf1.state_county
        acs_method = census_api_client.acs.state_county
        api_method_args = tuple(split_area)
    elif len(split_area) == 3:
        sf1_method = census_api_client.sf1.state_msa
        acs_method = None # msa data are unavailable in ACS dataset
        api_method_args = tuple(split_area[:2]) # truncating 3rd dummy parameter
    else:
        raise Exception("Cannot parse string '%s'" %area)
    for data_set, statistic_type in STATISTICS_OF_INTEREST:
        if data_set == "SF1":
            api_method = sf1_method
            api_params = sf1_api_params
        elif data_set == "ACS":
            if acs_method is None:
                continue
            api_method = acs_method
            api_params = acs_api_params
        else:
            raise Exception('Invalid dataset "%s" for statistic "%s"' %(data_set, statistic_type))
        print "Processing %s from %s" %(statistic_type, data_set)
        stat_data = []
        for i in range(0, len(api_params[statistic_type].keys()), 5):
            print "request #%s" %i
            j = min(len(api_params[statistic_type].keys()), i+5)
            part_res = cached_call(
                "%s>>>%s>>>%s>>>%s" %(data_set, area, statistic_type, i),
                api_method,
                tuple(api_params[statistic_type].keys()[i:j]),
                *api_method_args
            )[0]
            for key, value in part_res.items():
                if key in ("county", "state", "metropolitan statistical area/micropolitan statistical area"):
                    continue
                stat_data.append([api_params[statistic_type][key][0], api_params[statistic_type][key][1], value])
        res[statistic_type] = sorted(stat_data, key=lambda elem: elem[0])
    if request.GET.get("pdf") is not None:
        res["STATISTICS_OF_INTEREST"] = STATISTICS_OF_INTEREST
        res.update(convert_input_value_for_fred_app(area)) # adding region name data
        return wkhtml_pdf("statistic_report.html", res)
    if request.GET.get("html") is not None:
        res["STATISTICS_OF_INTEREST"] = STATISTICS_OF_INTEREST
        res.update(convert_input_value_for_fred_app(area)) # adding region name data
        return render_to_response("statistic_report.html", RequestContext(request, res))
    else:
        res = dumps(res)
        return HttpResponse(res)
