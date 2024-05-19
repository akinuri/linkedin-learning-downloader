import json
from helpers.general import input2, prog_exit
from helpers.course import *

def main():
    
    course_slug = input2("Enter the course URL or slug: ", validate=is_course_url)
    course_slug = get_course_slug(course_slug)
    
    course_json_data = get_course_json_data(course_slug)
    if isinstance(course_json_data, int):
        print("")
        print("Request to the URL failed: %s" % str(course_json_data))
        print("")
        return main()
    
    course_links = collect_json_data(course_json_data)
    load_videos_urls(course_links, course_slug)
    load_html_exercise_file_urls(course_links, course_slug)
    
    course_links_output = build_course_links_output(course_links)
    
    with open("Links.html", "w", encoding="utf8") as html_file:
        html_file.write(course_links_output)
    
    prog_exit("", "Done.")

main()
