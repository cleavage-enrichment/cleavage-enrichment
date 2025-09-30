# Installation
## Using Docker
1. Start docker on the host system.
2. Clone the repository and move to `/django_server`.
3. Run the django server by using for example `docker compose up`.

## Using Poetry
1. Install Poetry.
2. Clone the Repo.
3. Move to `/django_server`.
4. Run `poetry install`.
5. Run `poetry run python manage.py runserver`

## Using the cleavage package
1. Install the package with your favorite packet manager. For example with `pip install cleavviz`.
2. Import Cleaviz into your python code with `import cleavviz`.
3. See `/cleavviz/README.md`.

## For development
1. Do everything from the using Poetry section.
2. Install pnpm
3. Move to `/frontend`.
4. Run `pnpm start`

# For development
## build new frontend
- for production: `pnpm build`
- for development: `pnpm dev`

## update python packages
- update all: poetry update
- add something: poetry add ...
- lock: poetry lock

## after changing libraries:
`poetry lock` in `/cleavviz` and `/django_server`






