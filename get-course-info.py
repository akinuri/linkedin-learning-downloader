from pprint import pprint
from bs4 import BeautifulSoup
import requests

course_url = "https://www.linkedin.com/learning/tailwind-css-essential-training"

course_info = {}

course_info_field_lookup = {
    "Title" : ".top-card-layout__title",
    "Instructor" : {
        "selector" : "h2.top-card-layout__headline .top-card__headline-row-item",
        "index"    : 0,
        "format"   : lambda value: value.replace("With ", ""),
    },
    "Released" : {
        "selector" : "h2.top-card-layout__headline .top-card__headline-row-item",
        "index"    : 4,
        "format"   : lambda value: value.replace("Released: ", ""),
    },
    "Duration" : {
        "selector" : "h2.top-card-layout__headline .top-card__headline-row-item",
        "index"    : 2,
        "format"   : lambda value: value.replace("Duration: ", ""),
    },
    "Level" : {
        "selector" : "h2.top-card-layout__headline .top-card__headline-row-item",
        "index"    : 3,
        "format"   : lambda value: value.replace("Skill level: ", ""),
    },
    "Description" : ".course-details__description .show-more-less-html__markup",
    "Skills covered" : {
        "selector" : ":is(.course-overview-body__content-skills-item, .course-skills__skill-list-item)",
        "multiple" : True,
    },
    # "Contents" : "",
}

request = requests.get(course_url)

soup = BeautifulSoup(request.text, features="html.parser")

for field, selector in course_info_field_lookup.items():
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
    course_info[field] = value


pprint(course_info, sort_dicts=False)


input()

