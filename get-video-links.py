from helpers.course import *

# TODO: get slug as argument
course_slug = "tailwind-css-essential-training"

chapters_json_data = get_chapters_json_data(course_slug)
chapters = get_videos_slugs(chapters_json_data)
load_videos_urls(chapters, course_slug)

video_links_output = build_video_links_output(chapters)

with open("video-links.html", "w", encoding="utf8") as html_file:
    html_file.write(video_links_output)

print("Done.")
input()

