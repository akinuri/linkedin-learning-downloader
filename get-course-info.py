import requests
from bs4 import BeautifulSoup
from helpers.general import soup_auto_select
from helpers.course import course_info_fields_selectors, get_info_contents, build_info_output

# TODO: get slug as argument
course_slug = "tailwind-css-essential-training"

course_url = "https://www.linkedin.com/learning/%s" % course_slug
request = requests.get(course_url)
html = request.text

soup = BeautifulSoup(html, features="html.parser")

course_info = soup_auto_select(soup, course_info_fields_selectors)
get_info_contents(soup, course_info)

course_info_output = build_info_output(course_info)

with open("Info.txt", "w", encoding="utf8") as info_file:
    info_file.write(course_info_output)

print("Done.")
input()

