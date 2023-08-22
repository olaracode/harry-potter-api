<a href="https://www.breatheco.de"><img height="280" align="right" src="https://github.com/4GeeksAcademy/flask-rest-hello/blob/main/docs/assets/badge.png?raw=true"></a>

# Flask Boilerplate for Junior Developers

Create flask API's in minutes, [📹 watch the video tutorial](https://youtu.be/ORxQ-K3BzQA).

- [Extensive documentation here](https://start.4geeksacademy.com).
- Integrated with Pipenv for package managing.
- Fast deloyment to render.com or heroku with `$ pipenv run deploy`.
- Use of `.env` file.
- SQLAlchemy integration for database abstraction.

## 1) Installation

This template installs itself in a few seconds if you open it for free with Codespaces (recommended) or Gitpod.
Skip this installation steps and jump to step 2 if you decide to use any of those services.

> Important: The boiplerplate is made for python 3.10 but you can change the `python_version` on the Pipfile.

The following steps are automatically runned withing gitpod, if you are doing a local installation you have to do them manually:

```sh
pipenv install;
psql -U root -c 'CREATE DATABASE example;'
pipenv run init;
pipenv run migrate;
pipenv run upgrade;
```

## Endpoints
