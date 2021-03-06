import os
from random import randint

os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'tango_with_django_project.settings')
import django

django.setup()
from rango.models import Category, Page


def populate():
    # First, we will create lists of dictionaries containing the pages
    # we want to add into each category.
    # Then we will create a dictionary of dictionaries for our categories
    # This might seem a little but confusing, but it allows us to iterate
    # through each data structure, and add the data to our models

    python_pages = [
        {"title": "Official Python Tutorial",
         "url": "http://docs.python.org/2/tutorial/",
         "views": 10},
        {"title": "How to Think Like a Computer Scientist",
         "url": "http://www.greenteapress.com/thinkpython/",
         "views": 12},
        {"title": "Learn Python in 10 Minutes",
         "url": "http://www.korokithakis.net/tutorials/python/",
         "views": 9}
    ]

    django_pages = [
        {"title": "Official Django Tutorial",
         "url": "https://docs.djangoproject.com/en/1.9/intro/tutorial01/",
         "views": 13},
        {"title": "Django Rocks",
         "url": "http://www.djangorocks.com/",
         "views": 10},
        {"title": "How to Tango with Django",
         "url": "http://www.tangowithdjango.com/",
         "views": 8}]

    other_pages = [
        {"title": "Bottle",
         "url": "http://bottlepy.org/docs/dev/",
         "views": 10},
        {"title": "Flask",
         "url": "http://flask.pocoo.org",
         "views": 30}]

    cats = {"Python": {"pages": python_pages},
            "Django": {"pages": django_pages},
            "Other Frameworks": {"pages": other_pages}}

    # If you want to add more categories or pages,
    # add them to the dictionaries above

    # The code below goes through the cats dictionary, then adds each category,
    # and then adds all associated pages for that category.
    # http://docs.quantifiedcode.com/python-anti-patterns/readability/
    # for more information about how to iterate over a dictionary properly.

    for cat, cat_data in cats.items():
        c = add_cat(cat)
        if __name__ == '__main__':
            for p in cat_data["pages"]:
                add_page(c, p["title"], p["url"], p["views"])

    # Print out the categories we have added
    for c in Category.objects.all():
        for p in Page.objects.filter(category=c):
            print("- {0} - {1}".format(str(c), str(p)))


def add_page(cat, title, url, views):
    p = Page.objects.get_or_create(category=cat, title=title)[0]
    p.url = url
    p.views = views
    p.save()
    return p


def add_cat(name):
    likes = randint(0, 50)
    c = Category.objects.get_or_create(name=name)[0]
    setattr(c, 'likes', likes)
    c.save()
    return c


if __name__ == "__main__":
    print("Starting Rango population script ...")
    populate()
