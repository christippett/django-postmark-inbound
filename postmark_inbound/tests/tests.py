from base64 import b64encode
import os
import datetime
import json

from django.test import TestCase
from django.utils import timezone
from django.core.files.base import ContentFile
from django.utils.six import text_type, BytesIO
from django.utils import timezone

from rest_framework import serializers

from .. models import InboundMailAttachment, InboundMailHeader
from ..serializers import Base64FileField, AutoDateTimeField, InboundMailSerializer
from ..parsers import PostmarkJSONParser


class TestBase64FileField(TestCase):
    def setUp(self):
        class TestSerializer(serializers.Serializer):
            attachment = Base64FileField()
        self.Serializer = TestSerializer
        self.file_contents = b"This is attachment contents, base-64 encoded."
        self.encoded_contents = b64encode(self.file_contents).decode('UTF-8')

    def test_file_field_can_decode_base64_string(self):
        field = Base64FileField()
        decoded_contents = field.run_validation(self.encoded_contents)
        self.assertTrue(isinstance(decoded_contents, ContentFile))
        self.assertEqual(decoded_contents.read(), self.file_contents)

    def test_file_field_can_encode_base64_string(self):
        content_file = ContentFile(self.file_contents)
        base64_string = Base64FileField(encode_file=True).to_representation(content_file)
        self.assertTrue(isinstance(base64_string, text_type))
        self.assertEqual(base64_string, self.encoded_contents)


class TestAutoDateTimeField(TestCase):
    valid_inputs = {
        'Fri, 1 Aug 2014 16:45:32 -0400': datetime.datetime(2014, 8, 1, 20, 45, 32, tzinfo=timezone.UTC()),
        'Fri, 01 Aug 2014 16:45:32 -04:00': datetime.datetime(2014, 8, 1, 20, 45, 32, tzinfo=timezone.UTC()),
        '1:35pm, 1 Jan 2001': datetime.datetime(2001, 1, 1, 13, 35, tzinfo=timezone.UTC()),
        '2001-01-01 13:00': datetime.datetime(2001, 1, 1, 13, 00, tzinfo=timezone.UTC()),
        '13/1/2001 16:45:32': datetime.datetime(2001, 1, 13, 16, 45, 32, tzinfo=timezone.UTC()),
        '1/13/2001 16:45:32': datetime.datetime(2001, 1, 13, 16, 45, 32, tzinfo=timezone.UTC()),
        'Tuesday May 23, 1999 10:00pm': datetime.datetime(1999, 5, 23, 22, 0, tzinfo=timezone.UTC()),
    }
    invalid_inputs = ['abc', '2/x/2015', '13/13/2015']
    field = AutoDateTimeField()

    def test_valid_inputs(self):
        for input_value, expected_output in self.valid_inputs.items():
            self.field.run_validation(input_value) == expected_output

    def test_invalid_inputs(self):
        for input_value in self.invalid_inputs:
            with self.assertRaises(serializers.ValidationError):
                self.field.run_validation(input_value)


class TestInboundMailSerializer(TestCase):
    def setUp(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.example_json = open(os.path.join(BASE_DIR, 'example_2_attachments.json')).read()
        # Create serializer object from JSON data
        stream = BytesIO(self.example_json.encode())
        data = PostmarkJSONParser().parse(stream)
        self.serializer = InboundMailSerializer(data=data)

    def test_postmark_json_parser_maps_fields(self):
        """
        Test Postmark's JSON keys in camelCase map to model fields
        """
        field_map = {
            'From': 'from_email',
            'FromName': 'from_name',
            'To': 'to_email',
            'Cc': 'cc_email',
            'Bcc': 'bcc_email',
            'OriginalRecipient': 'original_recipient',
            'Subject': 'subject',
            'MessageID': 'message_id',
            'ReplyTo': 'reply_to',
            'MailboxHash': 'mailbox_hash',
            'Date': 'date',
            'TextBody': 'text_body',
            'HtmlBody': 'html_body',
            'StrippedTextReply': 'stripped_text_reply',
            'Tag': 'tag',
        }
        json_data = json.loads(self.example_json)
        self.serializer.is_valid(raise_exception=True)

        for source_key, destination_key in field_map.items():
            source = json_data[source_key]
            destination = self.serializer.initial_data[destination_key]
            self.assertTrue(
                source == destination,
                '%s (%s) does not equal %s (%s)'
                % (source_key, source, destination_key, destination)
            )

    def test_serializer_creates_attachments(self):
        self.serializer.is_valid(raise_exception=True)
        inbound_mail = self.serializer.save()
        count_attachments = inbound_mail.attachments.count()
        attachment = inbound_mail.attachments.all()[0]
        self.assertTrue(
            isinstance(
                attachment.__class__,
                InboundMailAttachment.__class__))
        self.assertEqual(count_attachments, 2)

    def test_serializer_creates_headers(self):
        self.serializer.is_valid(raise_exception=True)
        inbound_mail = self.serializer.save()
        count_headers = inbound_mail.attachments.count()
        header = inbound_mail.attachments.all()[0]
        self.assertTrue(
            isinstance(
                header.__class__,
                InboundMailHeader.__class__))
        self.assertTrue(count_headers > 0)
