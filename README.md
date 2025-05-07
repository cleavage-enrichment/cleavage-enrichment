# cleavage-enrichment


tools:
backend:
- django
- poetry for python version managing
frontend: react
poetry


# setup
- install poetry
- cd backend; poetry install; poetry run

# start django
poetry run python manage.py runserver

# update python packages
- poetry update

# repo build
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






