from helpers.general import input2, prog_exit
from helpers.course import *

def main():
    
    course_slug = input2("Enter the course URL or slug: ", validate=is_course_url)
    course_slug = get_course_slug(course_slug)
    
    chapters_json_data = get_chapters_json_data(course_slug)
    if isinstance(chapters_json_data, int):
        print("")
        print("Request to the URL failed: %s" % str(chapters_json_data))
        print("")
        return main()
    
    chapters = get_videos_slugs(chapters_json_data)
    load_videos_urls(chapters, course_slug)
    
    video_links_output = build_video_links_output(chapters)
    
    with open("video-links.html", "w", encoding="utf8") as html_file:
        html_file.write(video_links_output)
    
    prog_exit("", "Done.")

main()
