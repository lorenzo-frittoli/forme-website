
# ForMe Website

**NOT FINISHED YET**

Website for [ForMe](https://www.liceocassini.it/pages/forme.php), a yearly event at [Liceo Cassini](https://www.liceocassini.it/) highschool.

This website supports booking activities with limited availability, on multiple days, over multiple timespans of variable length.

There is a "Me" page, detailing all the activities one has booked.

It features different days for different types of users (ei: students and guests).

It supports randomly filling the unbooked timespans in a user's schedule.

## Deployment

To deploy the server for public use, follow [Flask's documentation](https://flask.palletsprojects.com/en/2.2.x/deploying/).

### Test Hosting

For testing purposes, you can host the website by running

```bash
flask run
```
If you want your server to be externally visible, use the `--host` argument, eg:

```bash
flask run --host=0.0.0.0
```
## Tech Stack

**Frontend:** HTML5, CSS, JavaScript, Django Template Language

**Backend:** Python with Flask

**Database:** SQLite3


## License

#TODO


## Authors

- [@lorenzo-frittoli](https://www.github.com/lorenzo-frittoli)

