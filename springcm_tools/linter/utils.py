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
        self.number = paragraph_number
        self.solo_tag = False
        self.merge_tags = None
        self.needs_link = False

    def process(self):
        global LINK_TYPES
        self.merge_tags = []

        # Get positions of all opening and closing <# #> directives
        open_directives = list(find_all(self.docx_paragraph.text, "<#"))
        close_directives = list(find_all(self.docx_paragraph.text, "#>"))

        assert len(open_directives) == len(close_directives) # TODO make sure no unmatched directives (TEST)
        directive_pairs = list(zip(open_directives, close_directives))
        # TODO make sure no nested directives (TEST)

        # TODO If there's a paragraph-level error, don't parse the merge tags.

        # Check if the tag is a paragraph-level tag, i.e., nothing else in it
        if len(directive_pairs) != 0:
            if directive_pairs[0][0] == 0 and directive_pairs[0][1] + 2 == len(self.docx_paragraph.text):
                self.solo_tag = True

        # Parse each directive into a MergeTag object
        # (cant easily have subclasses of MergeTag bc need to parse the tag before I know what type it is)
        for start, end in directive_pairs:
            end = end + 1 # this is because we want the position of the > character, not the # character in the #>
            # TODO There should be exactly one XML tag between those two directives. (TEST)
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
        return [tag for tag in self.merge_tags if tag.error]

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
    # TODO Go through each MergeTag object and collate all the errors
    # TODO Handle paragraph-level errors
    # TODO Handle tables and paragraphs inside of tables
    # TODO handle header / footer
    # TODO: schema does not enforce that TrackName can't start with XML
    # TODO: TableRow must be in the first cell of a table row
    # TODO: can't evaluate whether Test XPath is True or False without a params
    # TODO: Test whether spaces or weird formatting affect paragraph-level conditionals (i.e., does an extra space defeat it's "standing alone")