from helpers.general import dur_to_sec, dur_to_str, parse_dur_str, sec_to_dur

def get_contents(soup):
    chapters = []
    chaptersEls = soup.select(".toc-section")
    for chapterEl in chaptersEls:
        chapter = {
            "title"    : chapterEl.select_one("button").text.strip(),
            "videos"   : [],
            "duration" : "",
        }
        chapter_dur = 0
        chapterItems = chapterEl.select(".toc-item")
        for chapterItem in chapterItems:
            video = {
                "title"    : chapterItem.select_one(".table-of-contents__item-title").text.strip(),
                "duration" : chapterItem.select_one(".table-of-contents__item-duration").text.strip(),
            }
            if video["title"] == "Chapter Quiz":
                continue
            chapter_dur += dur_to_sec(parse_dur_str(video["duration"]))
            chapter["videos"].append(video)
        chapter["duration"] = dur_to_str(sec_to_dur(chapter_dur))
        chapters.append(chapter)
    return chapters

