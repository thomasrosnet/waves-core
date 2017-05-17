""" 
Compatibility file to enable dependents apps behaviour 
"""
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.admin import StackedInline

if 'jet' in settings.INSTALLED_APPS:
    from compat_jet import CompactInline
else:
    class CompactInline(StackedInline):
        """ Inherit base class """
        pass

if 'ckeditor' in settings.INSTALLED_APPS:
    from compat_ckeditor import *
else:
    from django.db import models

    class RichTextField(models.TextField):
        """ Override RichTextField """
        pass

if 'bootstrap_themes' in settings.INSTALLED_APPS:
    from compat_bootstrap_themes import list_themes, available_themes
else:
    available_themes = (
        ('default', 'Default'),
    )

    def list_themes():
        return available_themes

if 'constance' not in settings.INSTALLED_APPS:
    # from noconstance import config
    from waves.settings import waves_settings as config
    constance = None
else:
    import compat_constance
    import constance
    from constance import config

__all__ = ['config', "available_themes", "list_themes", "RichTextField", "CompactInline", 'constance']