from tortoise import migrations
from tortoise.migrations import operations as ops
from app.enums.finance import AccountTypes
from app.enums.offerings import DurationStatus, OfferingFrequency
from tortoise.fields.base import OnDelete
from tortoise import fields

class Migration(migrations.Migration):
    dependencies = [('main', '0003_add_clients_table')]

    initial = False

    operations = [
        ops.CreateModel(
            name='Duration',
            fields=[
                ('id', fields.BigIntField(generated=True, primary_key=True, unique=True, db_index=True)),
                ('gig', fields.ForeignKeyField('main.Gig', source_field='gig_id', db_constraint=True, to_field='id', related_name='durations', on_delete=OnDelete.CASCADE)),
                ('frequency', fields.CharEnumField(description='WEEKLY: WEEKLY\nMONTHLY: MONTHLY\nQUARTERLY: QUARTERLY\nEVERY_SIX_MONTHS: EVERY_SIX_MONTHS\nEVERY_TWELVE_MONTHS: EVERY_TWELVE_MONTHS', enum_type=OfferingFrequency, max_length=50)),
                ('status', fields.CharEnumField(default=DurationStatus.PENDING, description='PENDING: PENDING\nPARTIAL: PARTIAL\nPAID: PAID', enum_type=DurationStatus, max_length=50)),
                ('amount_paid', fields.DecimalField(default=0, max_digits=10, decimal_places=2)),
                ('start_at', fields.DatetimeField(auto_now=False, auto_now_add=False)),
                ('end_at', fields.DatetimeField(auto_now=False, auto_now_add=False)),
                ('created_at', fields.DatetimeField(auto_now=False, auto_now_add=True)),
            ],
            options={'table': 'durations', 'app': 'main', 'pk_attr': 'id', 'table_description': 'Duration model.'},
            bases=['Model'],
        ),
        ops.AddField(
            model_name='Gig',
            name='automatic_collection',
            field=fields.BooleanField(default=False),
        ),
        ops.AddField(
            model_name='Gig',
            name='card_token',
            field=fields.CharField(null=True, max_length=255),
        ),
        ops.AddField(
            model_name='Gig',
            name='resigned',
            field=fields.BooleanField(default=False),
        ),
        ops.AddField(
            model_name='Gig',
            name='signed_at',
            field=fields.DatetimeField(null=True, auto_now=False, auto_now_add=False),
        ),
        ops.AddField(
            model_name='Gig',
            name='valid_card',
            field=fields.BooleanField(default=False),
        ),
        ops.AlterField(
            model_name='Ledger',
            name='account_type',
            field=fields.CharEnumField(description='SYSTEM: SYSTEM\nGIG: GIG', enum_type=AccountTypes, max_length=50),
        ),
        ops.AlterField(
            model_name='Transaction',
            name='account_type',
            field=fields.CharEnumField(description='SYSTEM: SYSTEM\nGIG: GIG', enum_type=AccountTypes, max_length=50),
        ),
        ops.DeleteModel(name='Contract'),
    ]
