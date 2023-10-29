
# ForMe Website

Website for [ForMe](https://www.liceocassini.it/pages/forme.php), a yearly event at [Liceo Cassini](https://www.liceocassini.it/) highschool.

This website supports booking activities with limited availability, on multiple days, over multiple timespans of variable length.

There is a "Me" page, detailing all the activities one has booked.

It features different days for different types of users (ei: students and guests).

It supports randomly filling the unbooked timespans in a user's schedule.

## Releases
### Version 1.0
Do **NOT** use this version in production. It will likely scale poorly because of bad code that has since been fixed.

Supports basic features like separate guest and students accounts with differenta days, filling empty slots in schedules and other things.

## Deployment

### Setup
First, setup the database by running:
```bash
python manage.py make-db
```

Then, you can load student and activity data by running:
```bash
python manage.py load-students -f [filename]
python manage.py load-activities -f [filename]
```

### Hosting
For testing purposes, you can host the website by running

```bash
flask run
```
If you want your server to be externally visible, use the `--host` argument, eg:

```bash
flask run --host=0.0.0.0
```

To deploy the server for public use, follow [Flask's documentation](https://flask.palletsprojects.com/en/2.2.x/deploying/).


## Commands
The website comes with a suite of commands, both for local and remote usage.

Local commands are part of a CLI defined in `manage.py`. To see the available commands, run:
```bash
python manage.py --help
```

Remote commands are available in the admin area. The admin area is accessed at `/admin` and requires *both* an admin account and a password. Both can be configured in `constants.py`.

If there are accounts in the admin list which are not yet registered, the host will be notified.

## Tech Stack

**Frontend:** HTML5, CSS, JavaScript, Jinja Template Language

**Backend:** Python with Flask

**Database:** SQLite3


## License

This project is under the [Eclipse Public License](LICENSE) (v2.0).


## Authors

- [Lorenzo Frittoli](https://www.github.com/lorenzo-frittoli)
- [Luca Baglietto](https://www.github.com/BestCrazyNoob)

### Contributors

- [Giulia Aurora](https://www.github.com/Giulia-aurora)
