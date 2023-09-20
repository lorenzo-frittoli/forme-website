import sqlite3
import json

from constants import *


def main() -> None:
    """Make a new activity"""
    # Init activity details
    TITLE = "Title"
    TYPE = "Type"
    LENGTH = 2
    ABSTRACT = """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Maecenas volutpat blandit aliquam etiam erat velit scelerisque in. Praesent semper feugiat nibh sed pulvinar proin. Condimentum vitae sapien pellentesque habitant. Mi in nulla posuere sollicitudin aliquam. Commodo viverra maecenas accumsan lacus vel facilisis. Etiam non quam lacus suspendisse faucibus. Eu non diam phasellus vestibulum lorem sed risus ultricies tristique. Egestas pretium aenean pharetra magna ac placerat. Sed velit dignissim sodales ut eu sem integer vitae justo. Facilisi etiam dignissim diam quis enim lobortis scelerisque fermentum dui. In arcu cursus euismod quis.
    Lorem sed risus ultricies tristique nulla. Rhoncus urna neque viverra justo nec ultrices dui sapien. Venenatis urna cursus eget nunc. Tristique sollicitudin nibh sit amet commodo nulla facilisi. Rhoncus aenean vel elit scelerisque. Tempor commodo ullamcorper a lacus vestibulum sed arcu. In hendrerit gravida rutrum quisque non tellus orci ac auctor. Eget felis eget nunc lobortis mattis. Turpis nunc eget lorem dolor sed viverra ipsum nunc. Congue nisi vitae suscipit tellus. Pretium vulputate sapien nec sagittis aliquam malesuada bibendum. Rhoncus aenean vel elit scelerisque. Fermentum odio eu feugiat pretium nibh ipsum consequat nisl vel. Ut sem nulla pharetra diam sit. Natoque penatibus et magnis dis parturient. Lacus sed turpis tincidunt id aliquet risus feugiat in ante. Suspendisse in est ante in nibh mauris cursus. Pulvinar neque laoreet suspendisse interdum. Sollicitudin tempor id eu nisl nunc mi ipsum.
    Imperdiet dui accumsan sit amet nulla facilisi. Tellus elementum sagittis vitae et leo duis ut diam quam. Quam viverra orci sagittis eu volutpat. Nunc sed id semper risus in hendrerit. Fames ac turpis egestas maecenas pharetra convallis posuere. Ultrices vitae auctor eu augue ut. Amet nisl suscipit adipiscing bibendum est ultricies. Habitasse platea dictumst quisque sagittis purus sit. Lobortis mattis aliquam faucibus purus in. Viverra tellus in hac habitasse. Eu scelerisque felis imperdiet proin fermentum leo. Bibendum ut tristique et egestas quis ipsum suspendisse. Sit amet consectetur adipiscing elit pellentesque. Feugiat vivamus at augue eget arcu dictum varius duis at. Duis at tellus at urna condimentum mattis pellentesque id nibh. Morbi non arcu risus quis varius quam. Fringilla urna porttitor rhoncus dolor purus. Nisl nunc mi ipsum faucibus vitae aliquet nec ullamcorper sit. Pellentesque eu tincidunt tortor aliquam nulla facilisi cras fermentum odio. Quis commodo odio aenean sed.
    """

    timespans = ["08:00-10:00", "10:00-12:00"]
    AVAILABILITY = str(json.dumps({day: {t: 20 for t in timespans} for day in DAYS}))
    
    # Init sqlite3
    con = sqlite3.connect("database.db")
    cur = con.cursor()

    # Make new activity
    cur.execute("INSERT INTO activities (title, abstract, type, length, availability) VALUES (?, ?, ?, ?, ?);", (TITLE, ABSTRACT, TYPE, LENGTH, AVAILABILITY))
    con.commit()
    
    # Close connection (optional)
    cur.close()
    con.close()
    
    
if __name__ == '__main__':
    main()