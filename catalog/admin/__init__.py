# -*- coding: utf-8 -*-
from django.db import models
from django.contrib import admin
from catalog.models import TreeItem, Section, Item, TreeItemImage
from django.http import Http404, HttpResponse
from django.utils.html import escape
from django.contrib.admin.widgets import FilteredSelectMultiple
from catalog.admin.utils import get_connected, make_inline_admin


# Inlines for default models
class ImageInline(admin.StackedInline):
    model = TreeItemImage

class SectionInline(admin.StackedInline):
    model = Section
    prepopulated_fields = {'slug': ('name',)}

class ItemInline(admin.StackedInline):
    model = Item
    raw_id_fields = ('relative', 'sections')
    prepopulated_fields = {'slug': ('name',)}

class TreeItemAdmin(admin.ModelAdmin):
    model = TreeItem
    inlines = []
    
    def __init__(self, *args, **kwds):
        for model, modeladmin in get_connected():
            if not modeladmin:
                self.inlines.append(make_inline_admin(model))
            else:
                self.inlines.append(modeladmin)
        return super(TreeItemAdmin, self).__init__(*args, **kwds)    
    
    def response_change(self, request, obj):
        """
        Wrapper around Django ModelAdmin method to provide
        popup close on *edit* item
        """
        if ('_continue' not in request.POST) and ('_popup' in request.POST):
            pk_value = obj._get_pk_val()
            return HttpResponse('<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>' % \
                (escape(pk_value), escape(obj))) # escape() calls force_unicode.
        return super(ItemOptions, self).response_change(request, obj)

try:
    admin.site.register(TreeItem, TreeItemAdmin)
except admin.sites.AlreadyRegistered:
    pass
