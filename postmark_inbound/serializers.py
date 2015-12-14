import uuid
from base64 import b64decode, b64encode
from mimetypes import guess_extension

from django.utils.six import string_types
from django.core.files.base import ContentFile
from django.utils.translation import ugettext_lazy as _

import magic
from dateutil.parser import parse
from rest_framework import serializers

from .models import InboundMail, InboundMailHeader, InboundMailDetail, InboundMailAttachment
from .utils import InboundMailRelationMapper


class AutoDateTimeField(serializers.DateTimeField):
    """
    Attempt to parse incoming datetime value using `dateutil.parser.parse()`
    function.
    """
    def to_internal_value(self, value):
        try:
            parsed = parse(value)
        except (ValueError):
            pass
        else:
            return self.enforce_timezone(parsed)

        super(AutoDateTimeField, self).to_internal_value(value)


class Base64FileField(serializers.FileField):
    """
    Decode incoming file attachments encoded in Base64 and convert into a
    Django `ContentFile`.
    """
    default_error_messages = {
        'decode': _('File could not be decoded.'),
    }

    def __init__(self, *args, **kwargs):
        if 'encode_file' in kwargs:
            self.encode_file = kwargs.pop('encode_file')
        super(Base64FileField, self).__init__(*args, **kwargs)

    def to_internal_value(self, data):
        # Check to see if it's a base64 encoded file
        if isinstance(data, string_types):
            try:
                decoded_data = b64decode(data)
            except:
                self.fail('decode')

            file_ext = guess_extension(magic.from_buffer(decoded_data, mime=True).decode('UTF8'), strict=True)
            file_name = ''.join([uuid.uuid4().hex, file_ext])
            data = ContentFile(decoded_data, name=file_name)

        return super(Base64FileField, self).to_internal_value(data)

    def to_representation(self, value):
        encode_file = getattr(self, 'encode_file', False)

        if encode_file:
            return b64encode(value.read()).decode('UTF8')
        else:
            return super(Base64FileField, self).to_representation(value)


class InboundMailHeaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = InboundMailHeader
        fields = ('name', 'value')


class InboundMailDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = InboundMailDetail
        fields = ('email', 'name', 'mailbox_hash')


class InboundMailAttachmentSerializer(serializers.ModelSerializer):
    content = Base64FileField()

    class Meta:
        model = InboundMailAttachment
        fields = ('content', 'name', 'content_type', 'content_id', 'content_length')


class InboundMailSerializer(serializers.ModelSerializer):
    date = AutoDateTimeField()
    attachments = InboundMailAttachmentSerializer(many=True, required=False)
    headers = InboundMailHeaderSerializer(many=True, required=False)
    from_full = InboundMailDetailSerializer()
    to_full = InboundMailDetailSerializer(many=True)
    cc_full = InboundMailDetailSerializer(many=True)
    bcc_full = InboundMailDetailSerializer(many=True)

    class Meta:
        model = InboundMail
        fields = ('from_name', 'from_email', 'from_full', 'to_email', 'to_full', 'cc_email', 'cc_full', 'bcc_email', 'bcc_full', 'original_recipient', 'subject', 'message_id', 'reply_to', 'mailbox_hash', 'date', 'text_body', 'html_body', 'stripped_text_reply', 'tag', 'headers', 'attachments')
        extra_kwargs = {
            'date': {'input_formats': ['%a, %d %b %Y %H:%M:%S %z']}
        }

    def create(self, validated_data):
        header_data = validated_data.pop('headers')
        attachment_data = validated_data.pop('attachments')
        from_full_data = validated_data.pop('from_full')
        to_full_data = validated_data.pop('to_full')
        cc_full_data = validated_data.pop('cc_full')
        bcc_full_data = validated_data.pop('bcc_full')

        # Create mail object after data for related entities have been pop'd
        inbound_mail = InboundMail.objects.create(**validated_data)

        # Create relations with foreign key pointing to inbound_mail parent object
        rel_mapper = InboundMailRelationMapper(parent_mail=inbound_mail)

        # Create attachments
        rel_mapper.data(attachment_data).create_for(InboundMailAttachment)

        # Create headers
        rel_mapper.data(header_data).create_for(InboundMailHeader)

        # Create 'from' details
        rel_mapper.data(from_full_data).append({'address_type': 'FROM'}).create_for(InboundMailDetail)

        # Create 'to' details
        rel_mapper.data(to_full_data).append({'address_type': 'TO'}).create_for(InboundMailDetail)

        # Create 'cc' details
        rel_mapper.data(cc_full_data).append({'address_type': 'CC'}).create_for(InboundMailDetail)

        # Create 'bcc' details
        rel_mapper.data(bcc_full_data).append({'address_type': 'BCC'}).create_for(InboundMailDetail)

        return inbound_mail
