======================
JSON Convertible Model
======================

JSON Convertible Model is a Django app to replace models.Model and make it possible that models will
be able to return JSON-Objects directly without creating an new serializer class object.
It will not replace the awesome Django-Restframework package but sometimes it is to much afford for me.
Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "convertable_model" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'convertable_model',
    ]

2. Create your own models and choose "JSONConvertibleModel" as class to inherit from::

    class FooModel(JSONConvertibleModel):
        ...

2.1. Define which fields you want to use::

    class FooModel(JSONConvertibleModel):
        ...

        json_fields = '__all__'

    or

    class FooModel(JSONConvertibleModel):
        ...

        json_fields = ('field1', 'field2', )

2.2. Define the JSON-Key's if you want to give them a different name::

    class FooModel(JSONConvertibleModel):
        ...

        @jsonify_me
        def json_aliases(self):
            return {
                'foo1': 'IntegerField',
                'foo2': 'My_name'
            }

2.3 If you want to change the return value of the field::

    class FooModel(JSONConvertibleModel):
        ...

        @jsonify_me
        def prefix_foobar2(self):
        # import is the decorator and that the field name is written in "{foo}_{attribute}"
            return self.foobar2.upper()