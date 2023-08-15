import requests
from .general import dur_to_sec, dur_to_str, parse_dur_str, sec_to_dur

#region ==================== INFO

course_info_fields_selectors = {
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

def get_info_contents(soup, obj):
    chapters = []
    chaptersEls = soup.select(".toc-section")
    for chapterEl in chaptersEls:
        chapter = {
            "Title"    : chapterEl.select_one("button").text.strip(),
            "Videos"   : [],
            "Duration" : "",
        }
        chapter_dur = 0
        chapterItems = chapterEl.select(".toc-item")
        for chapterItem in chapterItems:
            video = {
                "Title"    : chapterItem.select_one(".table-of-contents__item-title").text.strip(),
                "Duration" : chapterItem.select_one(".table-of-contents__item-duration").text.strip(),
            }
            if video["Title"] == "Chapter Quiz":
                continue
            chapter_dur += dur_to_sec(parse_dur_str(video["Duration"]))
            chapter["Videos"].append(video)
        chapter["Duration"] = dur_to_str(sec_to_dur(chapter_dur))
        chapters.append(chapter)
    obj["Contents"] = chapters
    return chapters

def build_info_output(course):
    tab = "    "
    
    top_fields = ["Title", "Instructor", "Released", "Duration", "Level"]
    longest_field = max(top_fields, key=len)
    longest_field_output_len = len(longest_field) + (4 - len(longest_field) % 4)
    
    longest_video_name = ""
    for chapter in course["Contents"]:
        if len(chapter["Title"]) > len(longest_video_name):
            longest_video_name = chapter["Title"]
        for video in chapter["Videos"]:
            if len(video["Title"]) > len(longest_video_name):
                longest_video_name = video["Title"]
    longest_video_name_output_len = len(longest_video_name)
    longest_video_name_tab_offset = (4 - len(longest_video_name) % 4)
    if longest_video_name_tab_offset <= 1:
        longest_video_name_tab_offset = 4;
    longest_video_name_output_len += longest_video_name_tab_offset
    
    output_lines = []
    
    for field in top_fields:
        value = course[field]
        line = field.ljust(longest_field_output_len, " ") + ": " + value
        output_lines.append(line)
    
    output_lines.append("")
    output_lines.append("Description")
    output_lines.append("")
    output_lines.append(course["Description"])
    
    output_lines.append("")
    output_lines.append("Skills covered")
    for skill in course["Skills covered"]:
        output_lines.append(tab + skill)
    
    output_lines.append("")
    output_lines.append("Contents")
    output_lines.append(tab)
    
    is_contents_double_digit = len(course["Contents"]) - 1 > 9;
    
    for index, chapter in enumerate(course["Contents"]):
        chapter_title_parts = chapter["Title"].split(". ")
        chapter_title_parts = chapter_title_parts + ([None] * (2 - len(chapter_title_parts)))
        chapter_order, chapter_title = chapter_title_parts
        if chapter_order and chapter_title is None:
            chapter_title = chapter_order
            chapter_order = None
        if chapter_title in ["Introduction", "Welcome"]:
            chapter_order = "0"
        elif chapter_title == "Conclusion":
            chapter_order = str(index)
        if is_contents_double_digit:
            chapter_order = chapter_order.rjust(2, "0")
        chapter_title = chapter_order + ". " + chapter_title
        chapter_title = chapter_title.ljust(longest_video_name_output_len, " ")
        chapter_line = tab + chapter_title + tab + chapter["Duration"]
        output_lines.append(chapter_line)
        
        for video in chapter["Videos"]:
            video_title = video["Title"]
            video_title = video_title.ljust(longest_video_name_output_len)
            video_line = tab + tab + video_title + video["Duration"]
            output_lines.append(video_line)
        
        output_lines.append(tab)
    
    output = "\n".join(output_lines)
    
    return output

#endregion

