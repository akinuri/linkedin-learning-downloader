from pprint import pprint
from bs4 import BeautifulSoup
import requests
from helpers.general import auto_lookup
from helpers.course import course_fields_lookup_table, get_contents

course_url = "https://www.linkedin.com/learning/tailwind-css-essential-training"

request = requests.get(course_url)

soup = BeautifulSoup(request.text, features="html.parser")

course_info = auto_lookup(course_fields_lookup_table, soup)
get_contents(soup, course_info)

course_info["Contents"] = get_contents(soup)


pprint(course_info, sort_dicts=False)


input()

