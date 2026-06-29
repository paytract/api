from tortoise import migrations
from tortoise.migrations import operations as ops
import functools
from app.enums.finance import AccountTypes, SystemAccounts, TransactionTypes
from app.enums.offerings import OfferingFrequency
from json import dumps, loads
from tortoise.fields.base import OnDelete
from uuid import uuid4
from tortoise import fields
from tortoise.indexes import Index

class Migration(migrations.Migration):
    dependencies = [('main', '0001_add_user_table')]

    initial = False

    operations = [
        ops.CreateModel(
            name='Contract',
            fields=[
                ('id', fields.UUIDField(primary_key=True, default=uuid4, unique=True, db_index=True)),
                ('user', fields.ForeignKeyField('main.User', source_field='user_id', db_constraint=True, to_field='id', related_name='contracts', on_delete=OnDelete.CASCADE)),
                ('name', fields.CharField(max_length=255)),
                ('description', fields.TextField(null=True, unique=False)),
                ('client_name', fields.CharField(null=True, max_length=255)),
                ('client_email', fields.CharField(null=True, max_length=255)),
                ('price', fields.DecimalField(max_digits=10, decimal_places=2)),
                ('frequency', fields.CharEnumField(description='WEEKLY: WEEKLY\nMONTHLY: MONTHLY\nQUARTERLY: QUARTERLY\nEVERY_SIX_MONTHS: EVERY_SIX_MONTHS\nEVERY_TWELVE_MONTHS: EVERY_TWELVE_MONTHS', enum_type=OfferingFrequency, max_length=50)),
                ('metadata', fields.JSONField(default=list, encoder=functools.partial(dumps, separators=(',', ':')), decoder=loads)),
                ('mandate_id', fields.CharField(null=True, max_length=255)),
                ('is_valid', fields.BooleanField(default=False)),
                ('created_at', fields.DatetimeField(auto_now=False, auto_now_add=True)),
                ('ends_at', fields.DatetimeField(auto_now=False, auto_now_add=False)),
                ('signed_at', fields.DatetimeField(null=True, auto_now=False, auto_now_add=False)),
            ],
            options={'table': 'contracts', 'app': 'main', 'pk_attr': 'id', 'table_description': 'Contract model.'},
            bases=['Model'],
        ),
        ops.CreateModel(
            name='Gig',
            fields=[
                ('id', fields.UUIDField(primary_key=True, default=uuid4, unique=True, db_index=True)),
                ('user', fields.ForeignKeyField('main.User', source_field='user_id', db_constraint=True, to_field='id', related_name='gigs', on_delete=OnDelete.CASCADE)),
                ('name', fields.CharField(max_length=255)),
                ('description', fields.TextField(null=True, unique=False)),
                ('client_name', fields.CharField(null=True, max_length=255)),
                ('client_email', fields.CharField(null=True, max_length=255)),
                ('price', fields.DecimalField(max_digits=10, decimal_places=2)),
                ('frequency', fields.CharEnumField(description='WEEKLY: WEEKLY\nMONTHLY: MONTHLY\nQUARTERLY: QUARTERLY\nEVERY_SIX_MONTHS: EVERY_SIX_MONTHS\nEVERY_TWELVE_MONTHS: EVERY_TWELVE_MONTHS', enum_type=OfferingFrequency, max_length=50)),
                ('account_name', fields.CharField(null=True, max_length=255)),
                ('account_number', fields.CharField(null=True, max_length=20)),
                ('account_bank', fields.CharField(null=True, max_length=255)),
                ('created_at', fields.DatetimeField(auto_now=False, auto_now_add=True)),
                ('ends_at', fields.DatetimeField(auto_now=False, auto_now_add=False)),
            ],
            options={'table': 'gigs', 'app': 'main', 'pk_attr': 'id', 'table_description': 'Gig model.'},
            bases=['Model'],
        ),
        ops.CreateModel(
            name='Ledger',
            fields=[
                ('entry_id', fields.BigIntField(generated=True, primary_key=True, unique=True, db_index=True)),
                ('trace_id', fields.UUIDField()),
                ('account_type', fields.CharEnumField(description='SYSTEM: SYSTEM\nGIG: GIG\nCONTRACT: CONTRACT', enum_type=AccountTypes, max_length=50)),
                ('account_id', fields.UUIDField()),
                ('credit', fields.DecimalField(default=0, max_digits=10, decimal_places=2)),
                ('debit', fields.DecimalField(default=0, max_digits=10, decimal_places=2)),
                ('narration', fields.TextField(null=True, unique=False)),
            ],
            options={'table': 'ledgers', 'app': 'main', 'indexes': [Index(fields=['trace_id']), Index(fields=['account_id', 'account_type'])], 'pk_attr': 'entry_id', 'table_description': 'Ledger model.'},
            bases=['Model'],
        ),
        ops.CreateModel(
            name='SystemAccount',
            fields=[
                ('id', fields.UUIDField(primary_key=True, default=uuid4, unique=True, db_index=True)),
                ('name', fields.CharEnumField(unique=True, description='PAYTRACT_FEES: PAYTRACT_FEES', enum_type=SystemAccounts, max_length=50)),
            ],
            options={'table': 'system_accounts', 'app': 'main', 'pk_attr': 'id', 'table_description': 'System Account model.'},
            bases=['Model'],
        ),
        ops.CreateModel(
            name='Transaction',
            fields=[
                ('id', fields.UUIDField(primary_key=True, default=uuid4, unique=True, db_index=True)),
                ('trace_id', fields.UUIDField()),
                ('account_type', fields.CharEnumField(description='SYSTEM: SYSTEM\nGIG: GIG\nCONTRACT: CONTRACT', enum_type=AccountTypes, max_length=50)),
                ('account_id', fields.UUIDField()),
                ('amount', fields.DecimalField(max_digits=10, decimal_places=2)),
                ('narration', fields.TextField(null=True, unique=False)),
                ('type', fields.CharEnumField(description='CREDIT: CREDIT\nDEBIT: DEBIT', enum_type=TransactionTypes, max_length=10)),
            ],
            options={'table': 'transactions', 'app': 'main', 'indexes': [Index(fields=['trace_id']), Index(fields=['account_id', 'account_type', 'type'])], 'pk_attr': 'id', 'table_description': 'Transaction model.'},
            bases=['Model'],
        ),
    ]
