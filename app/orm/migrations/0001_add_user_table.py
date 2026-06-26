from tortoise import migrations
from tortoise.migrations import operations as ops
from uuid import uuid4
from tortoise import fields

class Migration(migrations.Migration):
    initial = True

    operations = [
        ops.CreateModel(
            name='User',
            fields=[
                ('id', fields.UUIDField(primary_key=True, default=uuid4, unique=True, db_index=True)),
                ('email', fields.CharField(unique=True, max_length=255)),
                ('password', fields.CharField(max_length=255)),
                ('first_name', fields.CharField(null=True, max_length=50)),
                ('last_name', fields.CharField(null=True, max_length=50)),
                ('phone', fields.CharField(null=True, max_length=20)),
                ('email_verified', fields.BooleanField(default=False)),
                ('date_joined', fields.DatetimeField(auto_now=False, auto_now_add=True)),
                ('last_active', fields.DatetimeField(auto_now=True, auto_now_add=False)),
            ],
            options={'table': 'user', 'app': 'main', 'pk_attr': 'id', 'table_description': 'User model.'},
            bases=['Model'],
        ),
    ]
