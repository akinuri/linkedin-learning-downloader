import requests
from bs4 import BeautifulSoup
from helpers.general import soup_auto_select, input2, prog_exit
from helpers.course import is_course_url, build_course_url, course_info_fields_selectors, get_info_contents, build_info_output

def main():
    
    course_slug = input2("Enter the course URL or slug: ", validate=is_course_url)
    course_url = build_course_url(course_slug)
    
    request = requests.get(course_url)
    if request.status_code != 200:
        print("")
        print("Request to the URL failed: %s" % str(request.status_code))
        print("")
        return main()
    
    html = request.text
    soup = BeautifulSoup(html, features="html.parser")
    
    course_info = soup_auto_select(soup, course_info_fields_selectors)
    get_info_contents(soup, course_info)
    
    course_info_output = build_info_output(course_info)
    with open("Info.txt", "w", encoding="utf8") as info_file:
        info_file.write(course_info_output)
    
    prog_exit("", "Done.")

main()
