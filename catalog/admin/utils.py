# -*- coding: utf-8 -*-
from catalog import settings as catalog_settings
from django.contrib import admin
from django.forms import ModelForm
from django.core.urlresolvers import get_mod_func
from django.core.exceptions import ImproperlyConfigured
from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404
from decimal import Decimal

def import_item(path, error_text):
    """Imports a model by given string. In error case raises ImpoprelyConfigured"""
    i = path.rfind('.')
    module, attr = path[:i], path[i+1:]
    try:
        return getattr(__import__(module, {}, {}, ['']), attr)
    except ImportError, e:
        raise ImproperlyConfigured('Error importing %s %s: "%s"' % (error_text, path, e))

def get_connected_models():
    '''
    Returns list like PAGE_CONNECTED_MODELS, but with imports classes
    and generates default ModelAdmin instead Nones
    '''
    def make_admin_class(model_class):
        class AutoAdmin(admin.ModelAdmin):
            model = model_class
        return AutoAdmin
    
    model_list = []
    for model_str, admin_str in catalog_settings.CATALOG_CONNECTED_MODELS:
        model_class = import_item(model_str, '')
        if admin_str is not None:
            model_list.append(
                (model_class, import_item(admin_str, ''))
            )
        else:
            model_list.append(
                (model_class, make_admin_class(model_class))
            )
    return model_list

def admin_permission_required(permission, login=True):
    def decorate(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.has_perm(permission):
                raise Http404('The requested admin page does not exist.')
            return view_func(request, *args, **kwargs)
        if login:
            wrapper = staff_member_required(wrapper)
        return wrapper
    return decorate

def get_instance_dict(instance, model_ext_admin):
    '''Base function converets instance to extjs dict'''
    data = {
        'id': instance.tree_id,
        'type': instance.__class__.__name__.lower(),
    }
    fields = model_ext_admin.fields
    for field in fields:
        value = getattr(instance, field, None)
        if callable(value):
            data[field] = value()
        else:
            data[field] = getattr(instance, field, None)
    return data

def get_grid_for_model(instance, model_ext_admin):
    '''Return dictionary with key/values as they sholud be in column model'''
    return get_instance_dict(instance, model_ext_admin)

def get_tree_for_model(instance, model_ext_admin):
    '''Return dictionary with key/values as they sholud be in column model'''
    if not model_ext_admin.tree_hide:
        data = get_instance_dict(instance, model_ext_admin)
        tree_text_attr = getattr(model_ext_admin, 'tree_text_attr')
        data.update({
            'text': getattr(instance, tree_text_attr, None),
            'leaf': model_ext_admin.tree_leaf,
        })
        return data

def encode_decimal(obj):
     if isinstance(obj, Decimal):
         return float(obj)
     raise TypeError(repr(o) + " is not JSON serializable")
