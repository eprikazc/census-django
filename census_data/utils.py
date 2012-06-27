from json import loads
from django.conf import settings


STATE_ABBREVIATIONS = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "District of Columbia": "DC",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
    "Puerto Rico": "PR",
    }


def convert_input_value_for_fred_app(input_string):
    """
    input_string=01 - state is 01
    input_string=01,001 - state is 01, county is 001
    input_string=01,001, - state is 01, MSA is 001
    """
    import os
    import redis
    redis_conn = redis.from_url(os.getenv('REDISTOGO_URL', 'redis://localhost:6379'))
    input_list = input_string.split(",")
    res = {}
    if len(input_list) == 1:
        state_id = input_list[0]
        county_id = msa_id = None
        res["county"] = res["msa"] = None
    elif len(input_list) == 2:
        state_id = input_list[0]
        county_id = input_list[1]
        msa_id = None
        res["msa"] = None
    elif len(input_list) == 3:
        state_id = input_list[0]
        county_id = None
        msa_id = input_list[1]
        res["county"] = None

    states = redis_conn.get("states")
    if states is None:
        raise Exception('"states" are not in redis cache!')
    states = loads(states)
    for state_data in states:
        if state_data['state'] == state_id:
            res['state'] = state_data['NAME']
            res['state_abbr'] = STATE_ABBREVIATIONS[state_data['NAME']]
            break
    else:
        raise Exception("State %s is not found" %state_id)

    if not res.has_key("county"):
        counties= redis_conn.get("counties")
        if counties is None:
            raise Exception('"counties" are not in redis cache!')
        counties = loads(counties)
        for county_data in counties:
            if county_data['county'] == county_id:
                res['county'] = county_data['NAME']
                break
        else:
            raise Exception("County %s is not found" %county_id)

    if not res.has_key("msa"):
        state_msas = redis_conn.get("msa,%s" %state_id)
        if state_msas is None:
            raise Exception('"MSAs" for %s are not in redis cache!' %state_id)
        state_msas = loads(state_msas)
        for msa_data in state_msas:
            if msa_data['metropolitan statistical area/micropolitan statistical area'] == msa_id:
                res['msa'] = msa_data['NAME']
                break
        else:
            raise Exception("MSA %s is not found" %msa_id)

    return res


def wkhtml_pdf(template_src, context_dict):
    from django.template import Context
    from django.template.loader import get_template
    from django.http import HttpResponse
    import os
    import subprocess

    template = get_template(template_src)
    context = Context(context_dict)
    rendered = template.render(context)

    full_temp_html_file_name = os.path.join(settings.STATIC_ROOT, 'temp_template.html')
    file = open(full_temp_html_file_name, 'w')
    file.write(rendered)
    file.close()

    wkhtmltopdf_command = os.path.join(settings.PROJECT_DIR, "..", "bin", os.getenv("WKHTMLTOPDF_BINARY", "wkhtmltopdf-i386"))
    wkhtmltopdf_command = '%s -O Landscape %s -' %(wkhtmltopdf_command, full_temp_html_file_name)
    popen = subprocess.Popen(
        wkhtmltopdf_command,
        bufsize=4096,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True
    )

    pdf_contents, err_contents = popen.communicate() #gets stdout and stderr
    print "err_contents: %s" %err_contents
    response = HttpResponse(pdf_contents, mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=statistic_report.pdf'
    return response
