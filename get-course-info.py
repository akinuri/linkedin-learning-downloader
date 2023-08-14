from pprint import pprint
from bs4 import BeautifulSoup
import requests
from helpers.general import auto_lookup
from helpers.course import get_contents

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
}

request = requests.get(course_url)

soup = BeautifulSoup(request.text, features="html.parser")

auto_lookup(course_info, course_info_field_lookup, soup)

course_info["Contents"] = get_contents(soup)


pprint(course_info, sort_dicts=False)


input()

