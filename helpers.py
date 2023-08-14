import re


def auto_lookup(obj, lookup_table, soup):
    for field, selector in lookup_table.items():
        value = ""
        prop = "text"
        if type(selector) is str:
            element = soup.select_one(selector)
        elif isinstance(selector, dict):
            index = selector["index"] if "index" in selector else None
            multiple = True if "multiple" in selector else False
            multiple = True if index is not None else multiple
            if multiple:
                element = soup.select(selector["selector"])
                if index is not None:
                    try:
                        element = element[index]
                    except:
                        element = None
            else:
                element = soup.select_one(selector["selector"])
            if "prop" in selector:
                prop = selector["prop"]
        if element:
            if isinstance(element, list):
                value = []
                for item in element:
                    if prop == "text":
                        value.append(item.text)
                    else:
                        value.append(item[prop])
            else:
                if prop == "text":
                    value = element.text
                else:
                    value = element[prop]
        if isinstance(selector, dict) and "format" in selector:
            value = selector["format"](value)
        if isinstance(value, list):
            for index, item in enumerate(value):
                value[index] = item.strip()
        else:
            value = value.strip()
        obj[field] = value

