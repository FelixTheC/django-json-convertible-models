#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@created: 17.02.20
@author: felix E.
"""

from django.db import models
import ujson
from django.db.models import QuerySet


def jsonify_me(func):
    def inner(*args, **kwargs):
        return func(*args, **kwargs)
    inner.json_me = True
    return inner


class JSONConvertibleModel(models.Model):
    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._json_fields = self.__class_json_fields()

    def __field_to_dict(self, field: any):
        if isinstance(field, (models.ForeignKey, models.OneToOneField)):
            try:
                return {field.attname.replace('_id', ''): str(getattr(self, field.attname.replace('_id', '')))}
            except (KeyError, AttributeError) as e:
                print(e)
                return {field.attname.replace('_id', ''): None}
        elif isinstance(field, models.ManyToManyField):
            related_obj = field.related_model
            if hasattr(related_obj, 'to_json_array'):
                related_ids = [i['id'] for i in getattr(self, field.attname).values('id')]
                return {field.attname: ujson.loads(related_obj.to_json_array(related_obj.objects.filter(id__in=related_ids)))}
            else:
                return {field.attname: None}
        else:
            return {field.attname: getattr(self, field.attname)}

    def __choosen_field(self, field: any):
        field_name = field.attname
        if '_id' in field_name:
            field_name = field_name.replace('_id', '')
        return field_name in self.json_fields

    def __class_json_fields(self):
        if self.json_fields == '__all__':
            fields = {}
            [fields.update(**self.__field_to_dict(field)) for field in self._meta.concrete_fields]
            if self.pk is not None:
                [fields.update(**self.__field_to_dict(field)) for field in self._meta.many_to_many]
        else:
            fields = {}
            [fields.update(**self.__field_to_dict(field)) for field in self._meta.concrete_fields if self.__choosen_field(field)]  # nopep8
            if self.pk is not None:
                [fields.update(**self.__field_to_dict(field)) for field in self._meta.many_to_many if self.__choosen_field(field)]  # nopep8
        return fields

    def __to_json(self):
        fields = self._json_fields
        for k, v in ((k, v) for k, v in vars(self.__class__).items() if hasattr(v, 'json_me') and 'aliases' not in k):
            obj_field = k.split('_')[-1]
            if obj_field in fields:
                fields[obj_field] = getattr(self, k)()
        for k, v in ((k, v) for k, v in vars(self.__class__).items() if hasattr(v, 'json_me') and 'aliases' in k):
            alias_dict = getattr(self, k)()
            for key_alias, alias_val in alias_dict.items():
                if key_alias in fields:
                    fields[alias_val] = fields[key_alias]
                    del fields[key_alias]
        return fields

    def to_json(self):
        return ujson.dumps(self.__to_json())

    @classmethod
    def to_json_array(cls, querset: QuerySet):
        return ujson.dumps([i.__to_json() for i in querset])
