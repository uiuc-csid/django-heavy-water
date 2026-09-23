# django-heavy-water

A reusable Django app that seeds your database with development and test data. Each app in your project defines *data builders*, and a single management command, `heavy_water`, runs the ones that apply to the current environment.

Requires Python 3.10+ and Django 4.2+.

## Installation

The package isn't on PyPI yet, so install it from GitHub:

```sh
pip install git+https://github.com/joshuata/django-heavy-water
```

Add it to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    "heavy_water",
]
```

## Usage

### Write a data builder

Create a `fixtures.py` module in any installed app and subclass `BaseDataBuilder`:

```python
# myapp/fixtures.py
from typing import Any

from django.conf import settings

from heavy_water import BaseDataBuilder

from myapp.models import Widget


class WidgetData(BaseDataBuilder):
    def should_run(self, *args: Any, **options: Any) -> bool:
        return settings.DEBUG

    def handle(self) -> None:
        self.get_or_create_superuser()
        Widget.objects.get_or_create(name="Sprocket")
```

### Run it

```sh
python manage.py heavy_water          # run all builders
python manage.py heavy_water --wipe   # flush the database first
```

`--wipe` uses Django's `flush` command, so it accepts `flush`'s options too, such as `--no-input`.

### How builders run

- The command runs every builder it finds whose `should_run()` returns `True`. By default it always does; override it to limit a builder to certain environments, as in the example above. `should_run()` receives the command's arguments and parsed options (such as `wipe` and `verbosity`), so you can use them as conditions too, for example `return options["wipe"]`.
- All builders run in one transaction, and each builder gets its own savepoint. If a builder raises, only its changes are rolled back and the other builders still run.
- If any builder failed, the command exits with an error listing them after committing the rest.

### Creating a superuser

`get_or_create_superuser()` returns the superuser identified by the user model's `USERNAME_FIELD`, creating it if it doesn't exist. Any argument you leave out falls back to the `HEAVY_WATER_SUPERUSER_*` settings below. Custom user models are supported, including ones that log in by email.

Pass `configure_user` to adjust the user after it's fetched or created; the user is saved afterwards:

```python
self.get_or_create_superuser(
    username="admin",
    configure_user=lambda user: setattr(user, "is_active", True),
)
```

> **Warning:** the default password is `rootroot`. Set `HEAVY_WATER_SUPERUSER_PASSWORD` before enabling any builder that creates a superuser outside local development.

## Settings

All settings are optional.

| Setting | Default | Description |
| --- | --- | --- |
| `HEAVY_WATER_FIXTURE_MODULE` | `["fixtures"]` | Submodule names searched for builders in each installed app. |
| `HEAVY_WATER_SUPERUSER_USERNAME` | `"root"` | Default login for `get_or_create_superuser()` (the email is used instead when the login field is the email). |
| `HEAVY_WATER_SUPERUSER_EMAIL` | `"root@example.com"` | Default email. |
| `HEAVY_WATER_SUPERUSER_PASSWORD` | `"rootroot"` | Default password. |
| `HEAVY_WATER_SUPERUSER_FIRST_NAME` | `"Root"` | Default first name, if the user model has the field. |
| `HEAVY_WATER_SUPERUSER_LAST_NAME` | `"User"` | Default last name, if the user model has the field. |

## Development

Development tooling is managed by [mise](https://mise.jdx.dev). It installs [uv](https://docs.astral.sh/uv/), [ruff](https://docs.astral.sh/ruff/) and [hk](https://hk.jdx.dev), and activates the project's `.venv`. Every development script is a mise task, so run everything through `mise run`.

First-time setup:

```sh
mise install     # install uv, ruff and hk
mise run setup   # create .venv with dev dependencies and install the pre-commit hook
```

Tasks:

| Command | What it does |
| --- | --- |
| `mise run setup` | Runs `sync` and `hooks`. |
| `mise run sync` | Installs the package and dev dependencies into `.venv`. |
| `mise run hooks` | Installs the hk pre-commit hook. |
| `mise run lint` | Runs all checks: ruff lint, ruff format, mypy and `uv lock --check`. The pre-commit hook runs the same checks. |
| `mise run fix` | Applies ruff fixes and formatting, and updates `uv.lock`. |
| `mise run test` | Runs the test suite with pytest. |
| `mise run typecheck` | Runs mypy in strict mode on the package. |
| `mise run build` | Builds the sdist and wheel into `dist/`. |

Run `mise tasks` to list them. To add a script, define it as a task in `mise.toml`.

The package ships a `py.typed` marker and is checked with mypy in strict mode, so new code must be fully type-annotated.

## License

BSD 3-Clause. See [LICENSE](LICENSE).
