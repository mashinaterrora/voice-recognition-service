DC = docker compose
EXEC = docker exec -it
LOGS = docker logs
ENV = --env-file .env
APP_FILE = docker/app.yaml
APP_CONTAINER = main-app
STORAGE = docker/storages.yaml

.PHONY: all
all:
	${DC} -f ${STORAGE} -f ${APP_FILE} ${ENV} up --build -d
	
.PHONY: app
app:
	${DC} -f ${APP_FILE} ${ENV} up --build -d

.PHONY: app-down
app-down:
	${DC} -f ${APP_FILE} down

.PHONY: app-shell
app-shell:
	${EXEC} ${APP_CONTAINER} bash

.PHONY: app-logs
app-logs:
	${LOGS} ${APP_CONTAINER} -f

.PHONY: storages
storages:
	${DC} -f ${STORAGE} ${ENV} up --build -d

.PHONY: storages-down
storages-down:
	${DC} -f ${STORAGE} down

.PHONY: db-rev
db-rev:
	${EXEC} ${APP_CONTAINER} alembic revision --autogenerate -m "$(m)"

.PHONY: db-upgrade
db-upgrade:
	${EXEC} ${APP_CONTAINER} alembic upgrade head

.PHONY: db-downgrade
db-downgrade:
	${EXEC} ${APP_CONTAINER} alembic downgrade $(s)

.PHONY: db-history
db-history:
	${EXEC} ${APP_CONTAINER} alembic history

.PHONY: test
ifeq ($(OS),Windows_NT)
	test:
		${EXEC} ${APP_CONTAINER} winpty pytest
else
	test:
		${EXEC} ${APP_CONTAINER} pytest || true
endif
