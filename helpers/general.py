import re
from math import floor


def auto_lookup(lookup_table, soup, obj = {}):
    for field, selector in lookup_table.items():
        value = ""
        prop = "text"
        if type(selector) is str:
            element = soup.select_one(selector)
        elif isinstance(selector, dict):
            index = selector["index"] if "index" in selector else None
            multiple = True if "multiple" in selector else False
            multiple = True if index is not None else multiple
            if multiple:
                element = soup.select(selector["selector"])
                if index is not None:
                    try:
                        element = element[index]
                    except:
                        element = None
            else:
                element = soup.select_one(selector["selector"])
            if "prop" in selector:
                prop = selector["prop"]
        if element:
            if isinstance(element, list):
                value = []
                for item in element:
                    if prop == "text":
                        value.append(item.text)
                    else:
                        value.append(item[prop])
            else:
                if prop == "text":
                    value = element.text
                else:
                    value = element[prop]
        if isinstance(selector, dict) and "format" in selector:
            value = selector["format"](value)
        if isinstance(value, list):
            for index, item in enumerate(value):
                value[index] = item.strip()
        else:
            value = value.strip()
        obj[field] = value
    return obj


def parse_dur_str(str):
    dur_h = 0
    dur_m = 0
    dur_s = 0
    match = re.search(r"(?:(\d+)h ?)?(?:(\d+)m ?)?(?:(\d+)s)?", str)
    if match:
        dur_h = int(match.group(1) or dur_h)
        dur_m = int(match.group(2) or dur_m)
        dur_s = int(match.group(3) or dur_s)
    dur = {
        "h" : dur_h,
        "m" : dur_m,
        "s" : dur_s,
    }
    return dur

def dur_to_sec(dur):
    return (dur["h"] * 60 * 60) + (dur["m"] * 60) + dur["s"]

def sec_to_dur(sec):
    dur_h = floor(sec / (60 * 60))
    sec -= dur_h * 60 * 60
    dur_m = floor(sec / 60)
    sec -= dur_m * 60
    dur_s = sec
    dur = {
        "h" : dur_h,
        "m" : dur_m,
        "s" : dur_s,
    }
    return dur

def dur_to_str(dur):
    parts = []
    if dur["h"] != 0:
        parts.append(str(dur["h"]) + "h")
    if dur["m"] != 0 or dur["h"] != 0:
        parts.append(str(dur["m"]) + "m")
    if dur["s"] != 0 or dur["m"] != 0 or dur["h"] != 0:
        parts.append(str(dur["s"]) + "s")
    result = " ".join(parts)
    return result

