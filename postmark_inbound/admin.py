from django.contrib import admin

from .models import InboundMail, InboundMailHeader, InboundMailAttachment, InboundMailDetail


class InboundMailAttachmentInline(admin.StackedInline):
    model = InboundMailAttachment
    extra = 0
    fields = ('name', 'content', 'content_type', 'content_length')
    readonly_fields = ('content_type', 'content_length')


class InboundMailHeaderInline(admin.TabularInline):
    model = InboundMailHeader
    extra = 0


class InboundMailDetailsInline(admin.TabularInline):
    model = InboundMailDetail
    extra = 0
    fields = ('address_type', 'name', 'email')
    readonly_fields = ('address_type',)


class InboundMailAdmin(admin.ModelAdmin):
    list_display = ('from_email', 'subject', 'date', 'has_attachment')
    list_filter = ('date',)
    search_fields = ('from_email', 'subject', 'text_body')
    inlines = [InboundMailDetailsInline, InboundMailAttachmentInline, InboundMailHeaderInline]
    fieldsets = (
        (None, {
            'fields': ('from_name', 'from_email', 'to_email', 'subject', 'text_body')}),
        ('Metadata', {
            'classes': ('collapse',),
            'fields': ('original_recipient', 'message_id', 'mailbox_hash', 'tag')})
    )


admin.site.register(InboundMail, InboundMailAdmin)
