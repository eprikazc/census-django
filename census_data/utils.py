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

fred_msas = ['Rapid City, SD', 'Cincinnati-Middletown, OH-KY-IN', 'Napa, CA', 'Little Rock-North Little Rock-Conway, AR', 'Pittsfield, MA', 'Great Falls, MT', 'Hanford-Corcoran, CA', 'Parkersburg-Marietta-Vienna, WV-OH', 'Wenatchee, WA', 'Reading, PA', 'Racine, WI', 'Elmira, NY', 'Spokane, WA', 'Bellingham, WA', 'Utica-Rome, NY', 'Baltimore-Towson, MD', 'York-Hanover, PA', 'Santa Barbara-Santa Maria-Goleta, CA', 'Gainesville, FL', 'Lawton, OK', 'San Antonio, TX', 'St. Cloud, MN', 'Worcester, MA', 'Harrisonburg, VA', 'Decatur, AL', 'Dothan, AL', 'Greeley, CO', 'Charleston, WV', 'Killeen-Temple-Fort Hood, TX', 'Stockton, CA', 'Portland-Vancouver-Beaverton, OR-WA', 'Huntsville, AL', 'Fayetteville, NC', 'Hattiesburg, MS', 'Ocean City, NJ', 'Cheyenne, WY', 'Jackson, MI', 'Alexandria, LA', 'Greenville-Mauldin-Easley, SC', 'San Luis Obispo-Paso Robles, CA', 'El Centro, CA', 'Jackson, MS', 'Chico, CA', 'Louisville-Jefferson County, KY-IN', 'Flagstaff, AZ', 'Raleigh-Cary, NC', 'Atlantic City-Hammonton, NJ', 'Shreveport-Bossier City, LA', 'Waterloo-Cedar Falls, IA', 'Las Vegas-Paradise, NV', 'Bay City, MI', 'Bangor, ME', 'Lincoln, NE', 'Myrtle Beach-North Myrtle Beach-Conway, SC', 'Sherman-Denison, TX', 'Lewiston, ID-WA', 'Montgomery, AL', 'Norwich-New London, CT', 'Charlottesville, VA', 'Jackson, TN', 'Tyler, TX', 'Rochester, MN', 'Dubuque, IA', 'Lewiston-Auburn, ME', 'McAllen-Edinburg-Mission, TX', 'Augusta-Richmond County, GA-SC', 'Youngstown-Warren-Boardman, OH-PA', 'Cape Coral-Fort Myers, FL', 'San Angelo, TX', 'Hickory-Lenoir-Morganton, NC', 'Battle Creek, MI', 'Bradenton-Sarasota-Venice, FL', 'Columbia, MO', 'Madera, CA', 'Akron, OH', 'Sumter, SC', 'Tuscaloosa, AL', 'Greensboro-High Point, NC', 'Hot Springs, AR', 'Jacksonville, FL', 'Valdosta, GA', 'Salinas, CA', 'La Crosse, WI-MN', 'Huntington-Ashland, WV-KY-OH', 'Evansville, IN-KY', 'Cleveland-Elyria-Mentor, OH', 'Tulsa, OK', 'Bloomington, IN', 'Dover, DE', 'Chattanooga, TN-GA', 'Sioux Falls, SD', 'Elizabethtown, KY', 'Waco, TX', 'Weirton-Steubenville, WV-OH', 'Cumberland, MD-WV', 'Monroe, LA', 'Portland-South Portland-Biddeford, ME', 'Chicago-Naperville-Joliet, IL-IN-WI', 'Provo-Orem, UT', 'Milwaukee-Waukesha-West Allis, WI', 'Nashville-Davidson--Murfreesboro--Franklin, TN', 'Fargo, ND-MN', 'Iowa City, IA', 'Greenville, NC', 'Springfield, IL', 'Rome, GA', 'Pine Bluff, AR', 'Bakersfield, CA', 'Yakima, WA', 'Miami-Fort Lauderdale-Pompano Beach, FL', 'Scranton--Wilkes-Barre, PA', 'Oklahoma City, OK', 'Bend, OR', 'Mount Vernon-Anacortes, WA', 'Decatur, IL', 'Buffalo-Niagara Falls, NY', 'Lakeland-Winter Haven, FL', 'Corpus Christi, TX', 'Billings, MT', 'Redding, CA', 'Ocala, FL', 'State College, PA', 'Columbus, IN', 'San Francisco-Oakland-Fremont, CA', 'Fond du Lac, WI', 'Bridgeport-Stamford-Norwalk, CT', 'Lake Havasu City-Kingman, AZ', 'Toledo, OH', 'Honolulu, HI', 'Atlanta-Sandy Springs-Marietta, GA', 'Kankakee-Bradley, IL', 'Athens-Clarke County, GA', 'Columbia, SC', 'Lima, OH', 'Sacramento--Arden-Arcade--Roseville, CA', 'Midland, TX', 'Minneapolis-St. Paul-Bloomington, MN-WI', 'Pittsburgh, PA', 'Boulder, CO', 'Olympia, WA', 'Altoona, PA', 'Bowling Green, KY', 'Baton Rouge, LA', 'Canton-Massillon, OH', 'Kalamazoo-Portage, MI', 'Oshkosh-Neenah, WI', 'College Station-Bryan, TX', 'Philadelphia-Camden-Wilmington, PA-NJ-DE-MD', 'Seattle-Tacoma-Bellevue, WA', 'Clarksville, TN-KY', 'Santa Rosa-Petaluma, CA', 'Palm Bay-Melbourne-Titusville, FL', 'Sandusky, OH', 'Lake Charles, LA', 'Owensboro, KY', 'Hinesville-Fort Stewart, GA', 'Omaha-Council Bluffs, NE-IA', 'Tucson, AZ', 'Florence, SC', 'Michigan City-La Porte, IN', 'Wichita, KS', 'Springfield, MO', 'San Diego-Carlsbad-San Marcos, CA', 'Jacksonville, NC', 'Lawrence, KS', 'Memphis, TN-MS-AR', 'Springfield, MA', 'Kansas City, MO-KS', 'Spartanburg, SC', 'Salem, OR', 'Roanoke, VA', 'Yuma, AZ', 'Binghamton, NY', 'Salt Lake City, UT', 'Wichita Falls, TX', 'Anchorage, AK', 'Providence-New Bedford-Fall River, RI-MA', 'Pascagoula, MS', 'Holland-Grand Haven, MI', 'Fayetteville-Springdale-Rogers, AR-MO', 'Cleveland, TN', 'Houston-Sugar Land-Baytown, TX', 'Wausau, WI', 'Davenport-Moline-Rock Island, IA-IL', 'Fairbanks, AK', 'Brunswick, GA', 'Carson City, NV', 'El Paso, TX', 'Hagerstown-Martinsburg, MD-WV', 'Monroe, MI', 'Danville, IL', 'Fort Wayne, IN', 'Amarillo, TX', 'Rochester, NY', 'South Bend-Mishawaka, IN-MI', 'Ames, IA', 'St. Joseph, MO-KS', 'Dalton, GA', 'Idaho Falls, ID', 'Punta Gorda, FL', 'Grand Forks, ND-MN', 'Lansing-East Lansing, MI', 'Medford, OR', 'Mobile, AL', 'Virginia Beach-Norfolk-Newport News, VA-NC', 'Tampa-St. Petersburg-Clearwater, FL', 'Johnstown, PA', 'Syracuse, NY', 'Muncie, IN', 'Victoria, TX', 'Bismarck, ND', 'Ogden-Clearfield, UT', 'Flint, MI', 'Orlando-Kissimmee, FL', 'Savannah, GA', 'Lafayette, IN', 'Abilene, TX', 'Blacksburg-Christiansburg-Radford, VA', 'Wilmington, NC', 'Florence-Muscle Shoals, AL', 'Naples-Marco Island, FL', 'Beaumont-Port Arthur, TX', 'Ithaca, NY', 'New Orleans-Metairie-Kenner, LA', 'Erie, PA', 'Port St. Lucie, FL', 'Albany, GA', 'Boise City-Nampa, ID', 'Des Moines-West Des Moines, IA', 'Yuba City, CA', 'Anderson, SC', 'Sheboygan, WI', 'Glens Falls, NY', 'Jefferson City, MO', 'Reno-Sparks, NV', 'Casper, WY', 'Kokomo, IN', 'Elkhart-Goshen, IN', 'Dayton, OH', 'Hartford-West Hartford-East Hartford, CT', 'Kingsport-Bristol-Bristol, TN-VA', 'Grand Rapids-Wyoming, MI', 'Rocky Mount, NC', 'Eugene-Springfield, OR', 'Santa Fe, NM', 'Riverside-San Bernardino-Ontario, CA', 'Winston-Salem, NC', 'Fresno, CA', 'Pensacola-Ferry Pass-Brent, FL', 'Corvallis, OR', 'Phoenix-Mesa-Scottsdale, AZ', 'Modesto, CA', 'Houma-Bayou Cane-Thibodaux, LA', 'Gainesville, GA', 'Santa Cruz-Watsonville, CA', 'Oxnard-Thousand Oaks-Ventura, CA', "Coeur d'Alene, ID", 'Mansfield, OH', 'Brownsville-Harlingen, TX', 'Deltona-Daytona Beach-Ormond Beach, FL', 'Albuquerque, NM', 'Lebanon, PA', 'Sebastian-Vero Beach, FL', 'Dallas-Fort Worth-Arlington, TX', 'Albany-Schenectady-Troy, NY', 'Joplin, MO', 'Duluth, MN-WI', 'Allentown-Bethlehem-Easton, PA-NJ', 'Morristown, TN', 'Laredo, TX', 'Lynchburg, VA', 'Salisbury, MD', 'Appleton, WI', 'Knoxville, TN', 'Farmington, NM', 'Tallahassee, FL', 'Charlotte-Gastonia-Concord, NC-SC', 'Trenton-Ewing, NJ', 'Poughkeepsie-Newburgh-Middletown, NY', 'St. Louis, MO-IL', 'Columbus, GA-AL', 'Wheeling, WV-OH', 'Charleston-North Charleston-Summerville, SC', 'Kennewick-Pasco-Richland, WA', 'Burlington-South Burlington, VT', 'Los Angeles-Long Beach-Santa Ana, CA', 'Detroit-Warren-Livonia, MI', 'Panama City-Lynn Haven, FL', 'Grand Junction, CO', 'Logan, UT-ID', 'Kingston, NY', 'Missoula, MT', 'Pocatello, ID', 'Merced, CA', 'Macon, GA', 'Warner Robins, GA', 'Gadsden, AL', 'Sioux City, IA-NE-SD', 'Las Cruces, NM', 'Janesville, WI', 'Auburn-Opelika, AL', 'Burlington, NC', 'Barnstable Town, MA', 'Danville, VA', 'Longview, TX', 'Goldsboro, NC', 'Gulfport-Biloxi, MS', 'Boston-Cambridge-Quincy, MA-NH', 'Colorado Springs, CO', 'Saginaw-Saginaw Township North, MI', 'Springfield, OH', 'Lexington-Fayette, KY', 'Odessa, TX', 'Birmingham-Hoover, AL', 'Terre Haute, IN', 'Palm Coast, FL', 'Manchester-Nashua, NH', 'Durham, NC', 'Eau Claire, WI', 'Vineland-Millville-Bridgeton, NJ', 'Harrisburg-Carlisle, PA', 'Indianapolis-Carmel, IN', 'Texarkana, TX-Texarkana, AR', 'Fort Smith, AR-OK', 'Peoria, IL', 'Morgantown, WV', 'Asheville, NC', 'Bremerton-Silverdale, WA', 'Visalia-Porterville, CA', 'Columbus, OH', 'Fort Walton Beach-Crestview-Destin, FL', 'Ann Arbor, MI', 'Prescott, AZ', 'Madison, WI', 'Muskegon-Norton Shores, MI', 'Niles-Benton Harbor, MI', 'Lubbock, TX', 'Anniston-Oxford, AL', 'Richmond, VA', 'St. George, UT', 'Bloomington-Normal, IL', 'Lafayette, LA', 'Rockford, IL', 'Longview, WA', 'Washington-Arlington-Alexandria, DC-VA-MD-WV', 'New Haven-Milford, CT', 'Green Bay, WI', 'Lancaster, PA', 'Topeka, KS', 'Johnson City, TN', 'Jonesboro, AR', 'Fort Collins-Loveland, CO', 'New York-Northern New Jersey-Long Island, NY-NJ-PA', 'Vallejo-Fairfield, CA', 'Pueblo, CO', 'Winchester, VA-WV', 'Cedar Rapids, IA', 'Williamsport, PA', 'San Jose-Sunnyvale-Santa Clara, CA', 'Austin-Round Rock, TX', 'Champaign-Urbana, IL', 'Anderson, IN', 'Denver-Aurora, CO']


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
                value = msa_data["NAME"]
                if value == "Wenatchee-East Wenatchee":
                    value = "Wenatchee"
                elif value == "San Antonio-New Braunfels":
                    value = "San Antonio"
                elif value == "Portland-Vancouver-Hillsboro":
                    value = "Portland-Vancouver-Beaverton"
                elif value == "Louisville/Jefferson County":
                    value = "Louisville-Jefferson County"
                elif value == "North Port-Bradenton-Sarasota":
                    value = "Bradenton-Sarasota-Venice"
                elif value == "Orlando-Kissimmee-Sanford":
                    value = "Orlando-Kissimmee"
                elif value == "Panama City-Lynn Haven-Panama City Beach":
                    value = "Panama City-Lynn Haven"
                elif value == "Crestview-Fort Walton Beach-Destin":
                    value = "Fort Walton Beach-Crestview-Destin"
                elif value == "Madera-Chowchilla":
                    value = "Madera"
                elif value == "Steubenville-Weirton":
                    value = "Weirton-Steubenville"
                elif value == "Chicago-Joliet-Naperville":
                    value = "Chicago-Naperville-Joliet"
                elif value == "Bakersfield-Delano":
                    value = "Bakersfield"
                elif value == "Phoenix-Mesa-Glendale":
                    value = "Phoenix-Mesa-Scottsdale"
                elif value == "Charlotte-Gastonia-Rock Hill":
                    value = "Charlotte-Gastonia-Concord"
                elif value == "Durham-Chapel Hill":
                    value = "Durham"
                elif value == "Austin-Round Rock-San Marcos":
                    value = "Austin-Round Rock"
                elif value == "Denver-Aurora-Broomfield":
                    value = "Denver-Aurora"

                res['msa'] = value

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
