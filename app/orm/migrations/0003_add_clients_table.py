from tortoise import migrations
from tortoise.migrations import operations as ops
from tortoise.fields.base import OnDelete
from uuid import uuid4
from tortoise import fields

class Migration(migrations.Migration):
    dependencies = [('main', '0002_add_offering_and_finance_tables')]

    initial = False

    operations = [
        ops.CreateModel(
            name='Client',
            fields=[
                ('id', fields.UUIDField(primary_key=True, default=uuid4, unique=True, db_index=True)),
                ('user', fields.ForeignKeyField('main.User', source_field='user_id', db_constraint=True, to_field='id', related_name='clients', on_delete=OnDelete.CASCADE)),
                ('name', fields.CharField(null=True, max_length=255)),
                ('email', fields.CharField(null=True, max_length=255)),
                ('metadata', fields.TextField(null=True, unique=False)),
                ('created_at', fields.DatetimeField(auto_now=False, auto_now_add=True)),
            ],
            options={'table': 'clients', 'app': 'main', 'pk_attr': 'id', 'table_description': 'Client model.'},
            bases=['Model'],
        ),
        ops.AddField(
            model_name='Contract',
            name='client',
            field=fields.ForeignKeyField('main.Client', source_field='client_id', null=True, db_constraint=True, to_field='id', related_name='contracts', on_delete=OnDelete.CASCADE),
        ),
        ops.RemoveField(model_name='Contract', name='client_email'),
        ops.RemoveField(model_name='Contract', name='client_name'),
        ops.RemoveField(model_name='Contract', name='metadata'),
        ops.AddField(
            model_name='Gig',
            name='client',
            field=fields.ForeignKeyField('main.Client', source_field='client_id', null=True, db_constraint=True, to_field='id', related_name='gigs', on_delete=OnDelete.CASCADE),
        ),
        ops.RemoveField(model_name='Gig', name='client_email'),
        ops.RemoveField(model_name='Gig', name='client_name'),
    ]
