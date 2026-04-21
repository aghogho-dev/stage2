import re
import pycountry

def parse_natural_language(query_str: str):
    filters = {}
    q = query_str.lower()

    if "female" in q: filters["gender"] = "female"
    elif "male" in q: filters["gender"] = "male"

    if "young" in q:
        filters["min_age"] = 16
        filters["max_age"] = 24


    if "adult" in q: filters["age_group"] = "adult"
    if "senior" in q: filters["age_group"] = "senior"
    if "child" in q: filters["age_group"] = "child"
    if "teenager" in q: filters["age_group"] = "teenager"

    above_match = re.search(r"above\s+(\d+)", q)
    if above_match:
        filters["min_age"] = int(above_match.group(1))


    for country in pycountry.countries:
        country_name = country.name.lower()
        official_name = getattr(country, 'official_name', '').lower()
        
        if country_name in q or (official_name and official_name in q):
            filters["country_id"] = country.alpha_2
            break 
        
    return filters if filters else None