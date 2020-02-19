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

    def __o2o_field(self, field: any) -> dict:
        field_name = field.attname.replace('_id', '')
        try:
            field_dict = {field_name: str(getattr(self, field_name))}
        except (KeyError, AttributeError) as e:
            print(e)
            field_dict = {field_name: None}
        return field_dict

    def __m2m_field(self, field: any) -> dict:
        field_name = field.attname
        related_obj = field.related_model
        related_ids = [i['id'] for i in getattr(self, field_name).values('id')]
        related_queryset = related_obj.objects.filter(id__in=related_ids)

        if hasattr(related_obj, 'to_json_array'):
            field_dict = {field_name: ujson.loads(related_obj.to_json_array(related_queryset))}
        else:
            field_dict = {field_name: [str(obj) for obj in related_queryset]}
        return field_dict

    def __field_to_dict(self, field: any) -> dict:
        if isinstance(field, (models.ForeignKey, models.OneToOneField)):
            field_dict = self.__o2o_field(field)
        elif isinstance(field, models.ManyToManyField):
            field_dict = self.__m2m_field(field)
        else:
            field_name = field.attname
            field_dict = {field_name: getattr(self, field_name)}
        return field_dict

    def __chosen_field(self, field: any):
        field_name = field.attname
        if '_id' in field_name:
            field_name = field_name.replace('_id', '')
        return field_name in self.json_fields

    def __class_json_fields(self):
        meta_fields = self._meta.concrete_fields
        m_2_m = self._meta.many_to_many
        chosen_field = self.__chosen_field
        field_to_dict = self.__field_to_dict

        fields = {}
        if self.json_fields == '__all__':
            [fields.update(**field_to_dict(field)) for field in meta_fields]
            if self.pk is not None:
                [fields.update(**field_to_dict(field)) for field in m_2_m]
        else:
            [fields.update(**field_to_dict(field)) for field in meta_fields if chosen_field(field)]
            if self.pk is not None:
                [fields.update(**field_to_dict(field)) for field in m_2_m if chosen_field(field)]
        return fields

    def __fields_optional_values(self, alias: bool = False):
        if alias:
            return [(k, v) for k, v in vars(self.__class__).items() if hasattr(v, 'json_me') and 'aliases' in k]
        return ((k, v) for k, v in vars(self.__class__).items() if hasattr(v, 'json_me') and 'aliases' not in k)

    def __to_json(self) -> dict:
        fields = self._json_fields
        for k, v in self.__fields_optional_values():
            obj_field = k.split('_')[-1]
            if obj_field in fields:
                fields[obj_field] = getattr(self, k)()

        alias_k = self.__fields_optional_values(True)
        if alias_k:
            alias_dict = getattr(self, alias_k[0][0])()
            for key_alias, alias_val in alias_dict.items():
                if key_alias in fields:
                    fields[alias_val] = fields[key_alias]
                    del fields[key_alias]
        return fields

    def to_json(self) -> any:
        return ujson.dumps(self.__to_json())

    @classmethod
    def to_json_array(cls, queryset: QuerySet) -> list:
        return ujson.dumps([i.__to_json() for i in queryset])
