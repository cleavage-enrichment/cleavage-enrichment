# software
- it works for uniprot fasta files

# cleavage-enrichment
tools:
backend:
- django
- poetry for python version managing
frontend:
- react
- vite
- pnpm


# setup
## django_server
- install poetry
- cd django_server; poetry install

# run server
## backend
- poetry run python manage.py runserver

## frontend
- pnpm install
- pnpm start

### build new frontend
- for production: pnpm build
- for development: pnpm dev

# run docker
- sudo apt-get install git-lfs
- git lfs install
- git clone

# update
## python packages
- update all: poetry update
- add something: poetry add ...
- lock: poetry lock

# how the repo was build
poetry new backend
cd backend
poetry config virtualenvs.in-project true --local
poetry add --group dev pytest
poetry add django
poetry add django-types django-stubs-ext
poetry run python  djpoe/manage.py migrate

cd ..
pnpm create vite@latest frontend -- --template react
cd frontend
pnpm install
pnpm run dev
followed https://aisaastemplate.com/blog/react-django-integration/






