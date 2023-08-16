import re
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


#region ==================== VIDEO LINKS

def get_user_cookies(path = "cookies.txt"):
    cookies = {
        "li_at" : "",
        "JSESSIONID" : "",
    }
    with open(path, "r", encoding="utf8") as cookies_file:
        lines = cookies_file.readlines()
        for line in lines:
            parts = line.split("=")
            key, value = parts + [None]*(2-len(parts))
            if key in ["li_at", "JSESSIONID"]:
                cookies[key] = value.replace("\"", "").strip()
    return cookies

def get_chapters_json_data(course_slug):
    course_url = (
        "https://www.linkedin.com/learning-api/detailedCourses"
        "?fields=chapters&q=slugs&courseSlug=%s" % course_slug
    )
    cookies = get_user_cookies()
    headers = {"Csrf-Token" : cookies["JSESSIONID"]}
    request = requests.get(course_url, headers=headers, cookies=cookies)
    content = request.json()
    return content

def get_videos_slugs(course_json_data):
    chapters = []
    for _chapter in course_json_data["elements"][0]["chapters"]:
        chapter = {
            "title" : _chapter["title"],
            "durationInSeconds" : _chapter["durationInSeconds"],
            "videos" : [],
        }
        for _video in _chapter["videos"]:
            video = {
                "title" : _video["title"],
                "slug" : _video["slug"],
                "durationInSeconds" : _video["durationInSeconds"],
                "streams" : {},
                "transcripts" : {},
            }
            chapter["videos"].append(video)
        chapters.append(chapter)
    return chapters

def get_video_json_data(course_slug, video_slug):
    video_url = (
        "https://www.linkedin.com/learning-api/videos"
        "?decorationId=com.linkedin.learning.api.deco.content.DecoratedVideo-67"
        "&parentSlug=%s&q=slugs&slug=%s" % (course_slug, video_slug)
    )
    cookies = get_user_cookies()
    headers = {"Csrf-Token" : cookies["JSESSIONID"]}
    request = requests.get(video_url, headers=headers, cookies=cookies)
    content = request.json()
    return content

def load_videos_urls(chapters, course_slug):
    for chapter in chapters:
        for video in chapter["videos"]:
            video_json_data = get_video_json_data(course_slug, video["slug"])
            video_metadata = video_json_data["elements"][0]["presentation"]["videoPlay"]["videoPlayMetadata"]
            streams = {}
            for _stream in video_metadata["progressiveStreams"]:
                streams[ _stream["height"] ] = _stream
            streams = dict(sorted(streams.items()))
            transcripts = {}
            for _transcript in video_metadata["transcripts"]:
                locale = "%s-%s" % (_transcript["locale"]["language"], _transcript["locale"]["country"])
                transcripts[locale] = _transcript
            video["streams"] = streams
            video["transcripts"] = transcripts

def build_video_links_output(chapters):
    html = []
    html.append(
        """
        <style>
            body {
                font-family: sans-serif;
                font-size: 14px;
                margin: 1em;
            }
            table {
                border-collapse: collapse;
                font-size: inherit;
            }
            th {
                background-color: hsla(0, 0%, 0%, 0.1);
            }
            th, td {
                padding: 0.3em 0.4em 0.2em;
                border: 1px solid silver;
            }
            tr.chapter td {
                background-color: hsla(0, 0%, 0%, 0.04);
                font-weight: 600;
                font-size: 0.9em;
                color: hsl(0deg 0% 0% / 90%);
            }
            tr.video td:first-child {
                padding-left: 2em;
            }
            #download-progress-indicator {
                --width: 0px;
                position: fixed;
                top: 0;
                left: 0;
                width: var(--width);
                height: 3px;
                background-color: forestgreen;
                transition: width 100ms;
                box-shadow: 0 1px 2px hsl(120deg 100% 10% / 25%),
                            0 2px 3px hsl(0deg 0% 100% / 25%);
            }
        </style>
        <div id="download-progress-indicator"></div>
        <table>
            <thead>
                <tr>
                    <th>Video</th>
                    <th>Duration</th>
                    <th>Streams</th>
                    <th>Transcripts</th>
                </tr>
            </thead>
            <tbody>
        """
    )
    for chapter in chapters:
        html.append(
            """
            <tr class="chapter">
                <td>%s</td>
                <td>%s</td>
                <td></td>
                <td></td>
            </tr>
            """ % (chapter["title"], dur_to_str(sec_to_dur(chapter["durationInSeconds"])))
        )
        for index, video in enumerate(chapter["videos"]):
            streams = []
            video_index = str(index + 1).rjust(2, "0")
            for height, stream in video["streams"].items():
                streams.append(
                    '<a href="%s" target="_blank" download="%s - %s.mp4" data-size="%s">%s</a> (%sM)' % (
                        stream["streamingLocations"][0]["url"],
                        video_index,
                        video["title"],
                        str(stream["size"]),
                        stream["height"],
                        "{:.1f}".format(stream["size"] / 1024 / 1024)
                    )
                )
            streams = ", \n".join(streams)
            transcripts = []
            for locale, transcript in video["transcripts"].items():
                transcripts.append(
                    '<a href="%s" download="%s - %s.vtt">%s.vtt</a>' % (
                        transcript["captionFile"],
                        video_index,
                        video["title"],
                        locale,
                    )
                )
            transcripts = ", \n".join(transcripts)
            html.append(
                """
                <tr class="video">
                    <td>%s - %s</td>
                    <td>%s</td>
                    <td>
                        %s
                    </td>
                    <td>
                        %s
                    </td>
                </tr>
                """ % (
                    video_index,
                    video["title"],
                    dur_to_str(sec_to_dur(video["durationInSeconds"])),
                    streams,
                    transcripts,
                )
            )
    html.append(
        """
            </tbody>
        </table>
        <script>
            function ajax(e,s){s.method=s.method||"GET",s.async=s.async||!0,s.user=s.user||null,s.password=s.password||null,s.data=s.data||null,s.responseType=s.responseType||"text";let a=new XMLHttpRequest;if(a.responseType=s.responseType,a.open(s.method,e,s.async,s.user,s.password),s.headers)for(let t in s.headers){let n=s.headers[t];a.setRequestHeader(t,n)}if(s.start&&(a.onloadstart=s.start.bind(a)),s.progress&&(a.onprogress=function(e){s.progress.call(a,e)}),s.uploadProgress&&(a.upload.onprogress=function(e){s.uploadProgress.call(a,e)}),s.after&&(a.onloadend=function(){s.after.call(this)}),(s.success||s.fail)&&(a.onreadystatechange=function(){a.readyState==XMLHttpRequest.DONE&&(200==a.status?s.success&&s.success.call(this):s.fail&&s.fail.call(this))}),s.timeout&&(a.timeout=s.timeout),s.data&&!(s.data instanceof FormData)){let o=new FormData;for(let r in s.data)o.append(r,s.data[r]);s.data=o}return a.send(s.data),a}
        </script>
        <script>
            let dpi = document.querySelector("#download-progress-indicator");
            let links = document.querySelectorAll("a[download]");
            links.forEach(link => {
                link.addEventListener("click", e => {
                    e.preventDefault();
                    coverntFiletoBlobAndDownload(link.href, link.download, link.dataset.size);
                });
            });
            const coverntFiletoBlobAndDownload = (fileURL, fileName, fileSize) => {
                ajax(fileURL, {
                    responseType: "arraybuffer",
                    start: () => dpi.style.setProperty("--width", "1px"),
                    progress : function (e) {
                        let progress = ((e.loaded / fileSize) * 100).toFixed(1);
                        dpi.style.setProperty("--width", progress + "%");
                    },
                    after: () => dpi.style.setProperty("--width", "0px"),
                    success: function () {
                        let blob = new Blob([this.response], {type:"video/mp4"})
                        const url = URL.createObjectURL(blob)
                        const a = document.createElement('a')
                        a.style.display = 'none'
                        a.href = url
                        a.download = fileName
                        document.body.appendChild(a)
                        a.click()
                        window.URL.revokeObjectURL(url)
                        a.remove()
                    }
                })
            }
        </script>
        """
    )
    html = "\n".join(html)
    return html

#endregion


#region ==================== URL

def is_course_url(url):
    if url.startswith("http"):
        pattern = r"^https?://(?:www.)?linkedin.com/learning/[a-z0-9]+(?:-[a-z0-9]+)*$"
        return bool(re.fullmatch(pattern, url))
    else:
        pattern = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
        return bool(re.fullmatch(pattern, url))

def build_course_url(url_or_slug):
    if url_or_slug.startswith("http"):
        return url_or_slug
    else:
        return "https://www.linkedin.com/learning/%s" % url_or_slug

#endregion

