import json
import os
import sys
from helpers.general import input2, prog_exit
from helpers.course import *

inputs = sys.argv[1:]
input = None
input_url = None
input_url_request_fail = False
if len(inputs):
    input = inputs[0]
    file_name, file_ext = os.path.splitext(os.path.basename(input))
    if file_ext:
        if file_ext != ".url":
            print("The input file extension isn't '.url'.")
        else:
            with open(input, "r") as url_file:
                content = url_file.read()
                match = re.search(r'URL=(.*)', content)
                if match:
                    input_url = match.group(1)

def main():
    
    global input_url_request_fail
    
    if input_url and input_url_request_fail is False:
        course_slug = input_url
        course_slug = get_course_slug(course_slug)
        print("Course URL: %s" % input_url)
    else:
        course_slug = input2("Enter the course URL or slug: ", validate=is_course_url)
        course_slug = get_course_slug(course_slug)
    
    course_json_data = get_course_json_data(course_slug)
    if isinstance(course_json_data, int):
        if input_url:
            input_url_request_fail = True
        print("")
        print("Request to the URL failed: %s" % str(course_json_data))
        print("")
        return main()
    
    os.makedirs("tmp", exist_ok=True)
    
    # debug: write
    with open("tmp/course.json", "w", encoding="utf8") as json_file:
        json_file.write(json.dumps(course_json_data, indent=4))
    
    course_links = collect_json_data(course_json_data)
    load_videos_urls(course_links, course_slug)
    load_html_exercise_file_urls(course_links, course_slug)
    
    # debug: write
    with open("tmp/links.json", "w", encoding="utf8") as json_file:
        json_file.write(json.dumps(course_links, indent=4))
    
    course_links_output = build_course_links_output(course_links)
    
    with open("Links.html", "w", encoding="utf8") as html_file:
        html_file.write(course_links_output)
    
    prog_exit("", "Done.")

main()
