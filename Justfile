run: 
	@fastapi dev

makemigrations *ARGS:
	@tortoise makemigrations {{ARGS}}

pending-migrations:
	@tortoise heads

migrate-up *ARGS:
	@tortoise upgrade {{ARGS}}

migrate-down *ARGS:
	@tortoise downgrade {{ARGS}}

scripts +ARGS:
	@python3 -m app.scripts.main {{ARGS}}
