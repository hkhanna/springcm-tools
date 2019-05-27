from django.test import SimpleTestCase

from docx import Document
from xml.etree import ElementTree as ET
from .utils import lint

def ms_wordify(input):
    document = Document()
    for paragraph in input.split("\n"):
        document.add_paragraph(paragraph)
    return document


class LintTests(SimpleTestCase):
    def test_unrecognized_tag(self):
        input = '<# <BadTagType Select="//Foo[text()=\'ok\']" /> #>'
        res = lint(ms_wordify(input))
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].error, "Unrecognized tag type: 'BadTagType'")


class ContentTagTests(SimpleTestCase):
    def test_pass(self):
        """Confirm easy case passes"""
        input = '<# <Content Select="//Foo" Optional="true" /> #>'
        res = lint(ms_wordify(input))
        self.assertEqual(len(res), 0)

    def test_self_closing_tags(self):
        """Test missing self-closing tag"""
        input = '<# <Content Select="//Foo" > #>'
        res = lint(ms_wordify(input))
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].error, "Missing self-closing tag />")

    def test_malformed_xml(self):
        """Test malformed xml"""
        input = '<# <Content Select="//Foo"Optional="true" /> #>'
        res = lint(ms_wordify(input))
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].error, "Malformed XML")

    def test_unrecognized_attributes(self):
        """Test unrecognized attributes"""
        input = '<# <Content Select="//Foo" Match="" /> #><# <Content Select="//Foo" Bar="" /> #>'
        res = lint(ms_wordify(input))
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0].error, "Invalid attributes")
        self.assertEqual(res[1].error, "Invalid attributes")

    def test_required_attributes(self):
        """Test required attributes are present"""
        # I think Select and Optional are required. TODO: investigate this
        input = '<# <Content Optional="true" /> #>'
        res = lint(ms_wordify(input))
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].error, "Invalid attributes")

        input = '<# <Content Select="//Foo" /> #>'
        res = lint(ms_wordify(input))
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].error, "Invalid attributes")

    def test_select(self):
        """Confirm the value of the Select attribute is valid XPath"""
        input = '<# <Content Select="\\badxpath" Optional="true" /> #>'
        res = lint(ms_wordify(input))
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].error, "Select attribute has invalid XPath")

    def test_optional(self):
        """Make sure the value of Optional is lowercase true or false"""
        input = '<# <Content Select="//Foo" Optional="True" /> #>'
        res = lint(ms_wordify(input))
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].error, "Invalid attributes")

    def test_track_name(self):
        """TrackName can contain only numbers, letters, spaces and periods, must start with a letter and cannot start with XML"""
        input = '<# <Content Select="//Foo" Optional="true" TrackName="Test Track Name 123.456 XML" /> #>'
        res = lint(ms_wordify(input))
        self.assertEqual(len(res), 0)

        input = '<# <Content Select="//Foo" Optional="true" TrackName="5est Track Name 123.456 XML" /> #>'
        res = lint(ms_wordify(input))
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].error, "Invalid attributes")

        input = '<# <Content Select="//Foo" Optional="true" TrackName="Te_t Track Name 123.456 XML" /> #>'
        res = lint(ms_wordify(input))
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].error, "Invalid attributes")

        input = '<# <Content Select="//Foo" Optional="true" TrackName="Te!t Track Name 123.456 XML" /> #>'
        res = lint(ms_wordify(input))
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].error, "Invalid attributes")


class TableRowTagTests(SimpleTestCase):
    def test_pass(self):
        """Confirm easy case passes"""
        input = '<# <TableRow Select="//Foo" Optional="true" /> #>'
        res = lint(ms_wordify(input))
        self.assertEqual(len(res), 0)

    def test_self_closing_tags(self):
        """Test missing self-closing tag"""
        input = '<# <TableRow Select="//Foo" > #>'
        res = lint(ms_wordify(input))
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].error, "Missing self-closing tag />")

    def test_malformed_xml(self):
        """Test malformed xml"""
        input = '<# <TableRow Select="//Foo"Optional="true" /> #>'
        res = lint(ms_wordify(input))
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].error, "Malformed XML")

    def test_unrecognized_attributes(self):
        """Test unrecognized attributes"""
        input = '<# <TableRow Select="//Foo" Match="" /> #><# <Content Select="//Foo" Bar="" /> #>'
        res = lint(ms_wordify(input))
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0].error, "Invalid attributes")
        self.assertEqual(res[1].error, "Invalid attributes")

    def test_required_attributes(self):
        """Test required attributes are present"""
        # I think Select and Optional are required. TODO: investigate this
        input = '<# <TableRow Optional="true" /> #>'
        res = lint(ms_wordify(input))
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].error, "Invalid attributes")

        input = '<# <TableRow Select="//Foo" /> #>'
        res = lint(ms_wordify(input))
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].error, "Invalid attributes")

    def test_select(self):
        """Confirm the value of the Select attribute is valid XPath"""
        input = '<# <TableRow Select="\\badxpath" Optional="true" /> #>'
        res = lint(ms_wordify(input))
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].error, "Select attribute has invalid XPath")

    def test_optional(self):
        """Make sure the value of Optional is lowercase true or false"""
        input = '<# <TableRow Select="//Foo" Optional="True" /> #>'
        res = lint(ms_wordify(input))
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].error, "Invalid attributes")

    def test_track_name(self):
        """TrackName can contain only numbers, letters, spaces and periods, must start with a letter and cannot start with XML"""
        input = '<# <TableRow Select="//Foo" Optional="true" TrackName="Test Track Name 123.456 XML" /> #>'
        res = lint(ms_wordify(input))
        self.assertEqual(len(res), 0)

        input = '<# <TableRow Select="//Foo" Optional="true" TrackName="5est Track Name 123.456 XML" /> #>'
        res = lint(ms_wordify(input))
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].error, "Invalid attributes")

        input = '<# <TableRow Select="//Foo" Optional="true" TrackName="Te_t Track Name 123.456 XML" /> #>'
        res = lint(ms_wordify(input))
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].error, "Invalid attributes")

        input = '<# <TableRow Select="//Foo" Optional="true" TrackName="Te!t Track Name 123.456 XML" /> #>'
        res = lint(ms_wordify(input))
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].error, "Invalid attributes")
