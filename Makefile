
export DJANGOPORT := 8001
export DEBUG := True
# you must update the value of HEROKUHOST
export HEROKUHOST := git:remote protected-bastion-43256
PSQL = psql
CMD = python3 manage.py
HEROKU = heroku run export SQLITE=1 &
# Add applications to APP variable as they are
# added to settings.py file
APP = models services restServer
export PGDATABASE = psi
## delete and create a new empty database
all: install_requirements update_models static

install_requirements:
	@echo install requirements
	pip3 install -r requirements.txt

clear_db:
	@echo Clear Database
	dropdb --if-exists $(PGDATABASE)
	createdb

# create alumnodb super user
create_super_user:
	$(CMD) createsu

populate:
	@echo populate database
	$(CMD) populate

runserver:
	$(CMD) runserver $(DJANGOPORT)

update_models:
	$(CMD) makemigrations
	$(CMD) migrate

restart_all: clear_db all populate create_super_user
#reset_db: clear_db update_models create_super_user

shell:
	@echo manage.py  shell
	@$(CMD) shell

dbshell:
	@echo manage.py dbshell
	@$(CMD) dbshell

addparticipants:
	@echo populate database
	python3 ./manage.py addparticipants

static:
	@echo manage.py collectstatic
	python3 ./manage.py collectstatic --noinput

fully_update_db:
	@echo del migrations and make migrations and migrate
	rm -rf */migrations
	python3 ./manage.py makemigrations $(APP) 
	python3 ./manage.py migrate

test_authentication:
	$(CMD) test models.test_authentication --keepdb

test_model:
	$(CMD) test models.test_models --keepdb

test_services:
	$(CMD) test create.test_services --keepdb

