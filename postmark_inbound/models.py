from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from .settings import inbound_mail_options as option


@python_2_unicode_compatible
class InboundMail(models.Model):
    from_name = models.CharField(blank=True, max_length=255)
    from_email = models.EmailField(max_length=254)
    to_email = models.CharField(blank=True, max_length=255)
    cc_email = models.CharField(blank=True, max_length=255)
    bcc_email = models.CharField(blank=True, max_length=255)
    original_recipient = models.CharField(blank=True, max_length=255)
    subject = models.CharField(blank=True, max_length=255)
    message_id = models.CharField(blank=True, max_length=255)
    reply_to = models.CharField(blank=True, max_length=255)
    mailbox_hash = models.CharField(blank=True, max_length=255)
    date = models.DateTimeField()
    text_body = models.TextField(blank=True)
    html_body = models.TextField(blank=True)
    stripped_text_reply = models.TextField(blank=True)
    tag = models.CharField(blank=True, max_length=255)

    def __str__(self):
        return ('%s: %s' % (self.from_email, self.subject))

    def has_attachment(self):
        return self.attachments.all().count() > 0
    has_attachment.boolean = True
    has_attachment.short_description = 'Attachment'

    @property
    def from_full(self):
        return self.address_details.get(address_type='FROM')

    @property
    def to_full(self):
        return self.address_details.filter(address_type='TO')

    @property
    def cc_full(self):
        return self.address_details.filter(address_type='CC')

    @property
    def bcc_full(self):
        return self.address_details.filter(address_type='BCC')


@python_2_unicode_compatible
class InboundMailHeader(models.Model):
    parent_mail = models.ForeignKey(InboundMail, related_name='headers', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    value = models.TextField(blank=True)

    def __str__(self):
        return ('%s: %s' % (self.name, self.value))


@python_2_unicode_compatible
class InboundMailAttachment(models.Model):
    parent_mail = models.ForeignKey(InboundMail, related_name='attachments', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    content_type = models.CharField(max_length=255)
    content = models.FileField(upload_to=option.ATTACHMENT_UPLOAD_TO)
    content_id = models.CharField(blank=True, max_length=255)
    content_length = models.IntegerField()

    def __str__(self):
        return ('%s (%s)' % (self.name, self.content_type))


# Declare sources of email addresses
ADDRESS_TYPES = tuple(map(lambda x: (x, x), ['FROM', 'TO', 'CC', 'BCC']))


@python_2_unicode_compatible
class InboundMailDetail(models.Model):
    parent_mail = models.ForeignKey(InboundMail, related_name='address_details', on_delete=models.CASCADE)
    address_type = models.CharField(choices=ADDRESS_TYPES, max_length=10)
    email = models.EmailField(blank=True, max_length=254)
    name = models.CharField(blank=True, max_length=255)
    mailbox_hash = models.CharField(blank=True, max_length=255)

    def __str__(self):
        return ('%s (%s)' % (self.email, self.address_type))
