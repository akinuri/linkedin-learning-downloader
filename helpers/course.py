from helpers.general import dur_to_sec, dur_to_str, parse_dur_str, sec_to_dur

course_fields_lookup_table = {
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

def get_contents(soup, obj):
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

