#!/usr/bin/env python3

import os
import os.path
import sys
import xml
import xml.sax
import yaml


def extract_md(filename):
    try:
        with open(filename, "r") as fh:
            return next(yaml.safe_load_all(fh))
    except IOError:
        return {}
    except yaml.YAMLError:
        return {}


def extract_xml(filename):
    parser = xml.sax.make_parser()
    handler = XmlHandler()
    parser.setContentHandler(handler)
    parser.parse(filename)
    return handler.metadata


class MdHandler(xml.sax.handler.ContentHandler):
    interesting_elements = ["title", "area", "workgroup"]
    def __init__(self):
        self.metadata = {}
        self.stack = []
        self.content = ""
        self.attrs = {}
        self.in_front = False

    def startElement(self, name, attrs):
        self.stack.append(name)
        self.attrs = attrs
        if self.stack == ["rfc", "front"]:
            self.in_front = True

    def endElement(self, name):
        pop_name = self.stack.pop()
        assert name == pop_name
        if self.in_front and pop_name == "front":
            self.in_front = False
        if self.in_front and name in self.interesting_elements:
            if name == "title" and self.attrs.get("abbrev", "").strip() != "":
                self.metadata["abbrev"] = self.attrs["abbrev"]
            self.metadata[name] = self.content.strip()
        self.content = ""
        self.attrs = {}

    def characters(self, data):
        self.content += data

    def processingInstruction(self, target, data):
        self.metadata[target.strip()] = data.strip()


extract_funcs = {".md": extract_md, ".xml": extract_xml}


if __name__ == "__main__":
    filename = sys.argv[1]
    target = sys.argv[2]
    if os.path.isfile(filename):
        fileext = os.path.splitext(filename)[1]
        extract_func = extract_funcs.get(fileext, lambda a: {})
        frontmatter = extract_func(filename)
        if target == "title" and frontmatter.get("abbrev", None) != None:
            value = frontmatter["abbrev"]
        else:
            value = frontmatter.get(target, "")
    else:
        value = ""
    print(value)
