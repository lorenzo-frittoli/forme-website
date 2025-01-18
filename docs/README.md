# ForMe Website

Website for ForMe, a yearly event at [Liceo Cassini](https://www.liceocassini.it/) highschool.
Hosted at <https://formecassini.eu.pythonanywhere.com>

## Features
- different user types with different features: students, guests, staff members and website admins
- booking activities of different length with limited availability on multiple days
- randomly filling the unbooked timespans in a user's schedule
- flexible user search
- user verification via qr codes
- easy setup from csv and json files using flask.cli
- admin page for remote management

## Testing
To test the website, run
```bash
python3 manage.py make-db
python3 manage.py load-students -f data/students_parsed.csv
python3 manage.py load-activities -f data/activities_parsed.json
flask run --debug
```

## Documentation 
The [documentation](./) is entirely in italian.

## Tech Stack

**Frontend:** HTML5, CSS, JavaScript, Jinja Template Language

**Backend:** Python with Flask

**Database:** SQLite3

## License

This project is under the [Eclipse Public License](LICENSE) (v2.0).

## Contribute / contact us
Open an [issue on github](https://github.com/lorenzo-frittoli/forme-website/issues/new) or contact us via email (found on our github profiles below).

## Authors

- [Lorenzo Frittoli](https://www.github.com/lorenzo-frittoli)
- [Luca Baglietto](https://www.github.com/BestCrazyNoob)

## Deployed by

- 2024/2025: [Lorenzo Frittoli](https://www.github.com/lorenzo-frittoli), [Luca Baglietto](https://www.github.com/BestCrazyNoob)
