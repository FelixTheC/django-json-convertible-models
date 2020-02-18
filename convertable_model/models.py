from datetime import datetime
from datetime import timedelta
from django.db import models
from math import pi

from convertable_model.json_model import JSONConvertibleModel
from convertable_model.json_model import jsonify_me


class FooModel(JSONConvertibleModel):
    FOO_CHOICES = (
        ('val1', 'Value1'),
        ('val2', 'Value2'),
    )
    foo1 = models.IntegerField(blank=True, null=True)
    foo2 = models.CharField(choices=FOO_CHOICES, max_length=5)
    foo3 = models.DecimalField(decimal_places=4, max_digits=10)
    foo4 = models.DateTimeField(blank=True, auto_now=True)

    json_fields = '__all__'

    @jsonify_me
    def json_aliases(self):
        return {
            'foo1': 'IntegerField',
            'foo2': 'My_name'
        }

    @jsonify_me
    def new_foo3(self):
        return pi

    def __str__(self):
        return f'{self.foo2}: {self.foo1 if self.foo1 is not None else 0}'


class BarModel(JSONConvertibleModel):
    BAR_CHOICES = (
        (1, 'Number_1'),
        (2, 'Number_2'),
    )
    bar1 = models.IntegerField(blank=True, null=True, choices=BAR_CHOICES)
    bar2 = models.CharField(blank=True, max_length=255)
    bar3 = models.DecimalField(decimal_places=4, max_digits=10)
    bar4 = models.DateTimeField(blank=True, auto_now=True)

    json_fields = ('bar1', 'bar2', 'bar4')

    @jsonify_me
    def jsn_bar2(self):
        return 'Hello World'


class FooBarModel(JSONConvertibleModel):
    foobar1 = models.ForeignKey(FooModel, on_delete=models.SET_NULL, null=True)
    foobar2 = models.CharField(blank=True, max_length=25)
    foobar3 = models.DecimalField(decimal_places=4, max_digits=10)
    foobar4 = models.DateTimeField(blank=True, auto_now=True)

    json_fields = ('foobar1', 'foobar2', 'foobar3')

    @jsonify_me
    def json_aliases(self):
        return {
            'foobar1': 'FooModel',
        }

    @jsonify_me
    def prefix_foobar2(self):
        # import is the decorator and that the field name is written in "{foo}_{attribute}"
        return self.foobar2.upper()

    @jsonify_me
    def j_foobar4(self):
        return datetime.utcnow() - timedelta(days=4)


class BarFooFooModel(JSONConvertibleModel):
    barfoo1 = models.ForeignKey(BarModel, on_delete=models.SET_NULL, null=True)
    barfoo4 = models.DateTimeField(blank=True, auto_now=True)

    json_fields = '__all__'

    def __str__(self):
        return f'{self.__class__.__name__}: {self.pk}'


class MixedFooBarModel(JSONConvertibleModel):
    foofoo = models.ManyToManyField(FooModel)
    barbar = models.ManyToManyField(BarModel)
    barfoo = models.ForeignKey(BarFooFooModel, on_delete=models.DO_NOTHING)

    json_fields = '__all__'
