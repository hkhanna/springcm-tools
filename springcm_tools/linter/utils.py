from django.apps import apps

from collections import defaultdict
from lxml import etree as ET
from docx import Document
from environ import Path

LINK_TYPES = {
    "Conditional": "EndConditional"
}
LINK_TYPES.update({ v:k for k,v in LINK_TYPES.items() })


def find_all(string, substring):
    start = 0
    while True:
        start = string.find(substring, start)
        if start == -1:
            return
        yield start
        start += len(substring)

class MergeTag:
    def __init__(self, start, end, paragraph):
        self.error = None
        self.error_raw = None
        self.directive_string = paragraph.text[start:end + 1]
        self.linked_tag = None
        self.type = None

        # Lop off the directives and strip whitespace
        self.tag_string = self.directive_string[2:]
        self.tag_string = self.tag_string[:-2]
        self.tag_string = self.tag_string.strip()

        # Replace Word's curly quotes with regular ones
        self.tag_string = self.tag_string.replace(u"\u201D", "\"")
        self.tag_string = self.tag_string.replace(u"\u201C", "\"")
        self.tag_string = self.tag_string.replace(u"\u2019", "'")
        self.tag_string = self.tag_string.replace(u"\u2018", "'")

        # Confirm tag is self closing />
        if self.tag_string[-2:] != "/>":
            self.error = "Missing self-closing tag />"
            return

        # Parse the tag into an XML element
        try:
            self.elem = ET.fromstring(self.tag_string)
        except ET.ParseError: 
            # Catch malformed XML
            self.error = "Malformed XML"
            return
        
        self.type = self.elem.tag

        rng_filename = Path(apps.get_app_config('linter').path)("tags.rng")
        relaxng_doc = ET.parse(rng_filename)
        relaxng = ET.RelaxNG(relaxng_doc)

        if not relaxng(self.elem):
            self.extract_relaxng_validation_error(relaxng.error_log)
            return

        if "Select" in self.elem.attrib:
            xpath = self.elem.attrib["Select"]
            try:
                ET.XPath(xpath)
            except ET.XPathError:
                self.error = "Select attribute has invalid XPath"
                return

        if "Test" in self.elem.attrib:
            xpath = self.elem.attrib["Test"]
            try:
                ET.XPath(xpath)
            except ET.XPathError:
                self.error = "Test attribute must be valid XPath that returns true or false"
                return

        # SuppressListItem must appear in a list
        if self.type == "SuppressListItem":
            pPr = paragraph._p.get_or_add_pPr()
            if pPr.numPr is None or pPr.numPr.numId is None:
                self.error = "SuppressListItem must appear in a bullet or ordered list item"
                return

    def extract_relaxng_validation_error(self, error_log):
        if error_log.last_error.type_name == "RELAXNG_ERR_ATTRVALID" or error_log.last_error.type_name == "RELAXNG_ERR_INVALIDATTR":
            self.error = "Invalid attributes"
            self.error_raw = error_log.last_error.message
        elif error_log.last_error.type_name == "RELAXNG_ERR_ELEMWRONG":
            msg = error_log.last_error.message 
            self.error = f"Unrecognized tag type: '{msg.split()[-2]}'"
            self.error_raw = error_log.last_error.message
        else:
            self.error = "Unknown error: " + error_log.last_error.type_name + " " + error_log.last_error.message

    @classmethod
    def match_tags(cls, merge_tags, inline=True):
        link_stack = { k: [] for k in LINK_TYPES }
        for tag in merge_tags:
            if tag.type in link_stack:
                countertag_type = LINK_TYPES[tag.type]
                if len(link_stack[countertag_type]) != 0:
                # See if there's a matching tag
                    countertag = link_stack[countertag_type].pop()
                    tag.linked_tag = countertag
                    countertag.linked_tag = tag
                else:
                # If not, add it to the stack for a future match
                    link_stack[tag.type].append(tag)

        # Now, set the error on any unmatched inline tags
        for type in link_stack:
            for tag in link_stack[type]:
                if inline:
                    tag.error = f'Unmatched inline {type} tag' 
                else:
                    tag.error = f'Unmatched paragraph-level {type} tag'

class Paragraph:
    def __init__(self, docx_paragraph, paragraph_number):
        self.docx_paragraph = docx_paragraph
        self.paragraph_number = paragraph_number
        self.error = None
        self.solo_tag = False
        self.merge_tags = None
        self.needs_link = False

    def process(self):
        self.merge_tags = []

        # Get positions of all opening and closing <# #> directives
        open_directives = list(find_all(self.docx_paragraph.text, "<#"))
        close_directives = list(find_all(self.docx_paragraph.text, "#>"))

        # Test for paragraph-level errors
        # Don't parse merge tags if these are encountered.
        if len(open_directives) != len(close_directives):
            self.error = "Unmatched #> or <# directive"
            return

        for index in range(len(open_directives) - 1):
            if open_directives[index + 1] < close_directives[index]:
                self.error = "Nested #> or <# directives not allowed"
                return

        directive_pairs = list(zip(open_directives, close_directives))
        # Check if the tag is a paragraph-level tag, i.e., nothing else in it
        # Need to trim whitespace because it does not interfere with paragraph-level determination
        trimmed_text = self.docx_paragraph.text.strip()
        open_directive_trimmed = list(find_all(trimmed_text, "<#"))
        close_directive_trimmed = list(find_all(trimmed_text, "#>"))

        if len(directive_pairs) != 0:
            if open_directive_trimmed[0] == 0 and close_directive_trimmed[0] + 2 == len(trimmed_text):
                self.solo_tag = True

        # Parse each directive into a MergeTag object
        # (cant easily have subclasses of MergeTag bc need to parse the tag before I know what type it is)
        for start, end in directive_pairs:
            end = end + 1 # this is because we want the position of the > character, not the # character in the #>
            self.merge_tags.append(MergeTag(start, end, self.docx_paragraph))

        # If there are any tag errors, don't bother processing links.
        # Because it gives misleading unmatched links errors.
        for tag in self.merge_tags:
            if tag.error:
                return

        if self.solo_tag and self.merge_tags[0].type in LINK_TYPES:
        # If this is a paragraph-level conditional tag, flag it for processing later
            self.needs_link = True
        else:
        # Otherwise, process the tags in the paragraph and link them where appropriate.
            MergeTag.match_tags(self.merge_tags)

    def errors(self):
        if self.error:
            return [(self.paragraph_number, self)]
        else:
            return [(self.paragraph_number, tag) for tag in self.merge_tags if tag.error]

def lint(document):
    blocks = []
    doc_errors = []

    for index, docx_paragraph in enumerate(document.paragraphs):
        block = Paragraph(docx_paragraph, index)
        block.process()
        blocks.append(block)

    solo_tags_to_match = [block.merge_tags[0] for block in blocks if block.needs_link]
    MergeTag.match_tags(solo_tags_to_match, inline=False)

    for block in blocks:
        doc_errors.extend(block.errors())

    return doc_errors