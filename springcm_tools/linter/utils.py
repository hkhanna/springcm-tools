from django.apps import apps

from collections import defaultdict
from lxml import etree as ET
from docx import Document
from environ import Path

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


       # TODO Each Conditional (and repeat?) tag has a EndConditional tag either (1) in the same paragraphs or (2) in their own separate paragraphs. (TEST)

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


def lint(document):
    doc_errors = []

    for paragraph in document.paragraphs:
        # Get positions of all opening and closing <# #> directives
        open_directives = list(find_all(paragraph.text, "<#"))
        close_directives = list(find_all(paragraph.text, "#>"))

        assert len(open_directives) == len(close_directives) # TODO make sure no unmatched directives (TEST)
        directive_pairs = zip(open_directives, close_directives)
        # TODO make sure no nested directives (TEST)

        # TODO If there's a paragraph-level error, don't parse the merge tags.

        # Parse each directive into a MergeTag object
        # (cant easily have subclasses of MergeTag bc need to parse the tag before I know what type it is)
        for start, end in directive_pairs:
            end = end + 1 # this is because we want the position of the > character, not the # character in the #>
            # TODO There should be exactly one XML tag between those two directives. (TEST)
            merge_tag = MergeTag(start, end, paragraph)
            if merge_tag.error:
                doc_errors.append(merge_tag)

        # TODO iterate through all tags and link the ones that need to be linked (TEST)

    return doc_errors
    # TODO Go through each MergeTag object and collate all the errors
    # TODO Handle paragraph-level errors
    # TODO Handle tables and paragraphs inside of tables
    # TODO handle header / footer
    # TODO: schema does not enforce that TrackName can't start with XML
    # TODO: TableRow must be in the first cell of a table row
    # TODO: can't evaluate whether Test XPath is True or False without a params