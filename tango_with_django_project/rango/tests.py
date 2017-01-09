from django.test import TestCase
from rango.models import Category
from django.core.urlresolvers import reverse


# Helpers

def add_cat(name, views, likes):
    c = Category(name=name, views=views, likes=likes)
    setattr(c, 'views', views)
    setattr(c, 'likes', likes)
    c.save()
    return c


# Create your tests here.

class CategoryMethodTests(TestCase):
    def test_ensure_views_are_positive(self):
        # ensure_views_are_positive should result True for categores
        # where views are zero or positive
        cat = Category(name="test", views=1, likes=0)
        cat.save()
        self.assertEqual((cat.views >= 0), True)

    def test_slug_line_creation(self):
        # slug_line_creation checks to make sure that when we add
        # a category, an appropriate slug line is created
        cat = Category(name='Random Category String')
        cat.save()
        self.assertEqual(cat.slug, 'random-category-string')


class IndexViewTests(TestCase):
    def test_index_view_with_no_categories(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "There are no categories present.")
        self.assertQuerysetEqual(response.context['categories'], [])

    def test_index_view_with_categories(self):
        add_cat('testro', 1, 1)

        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

        num_cats = len(response.context['categories'])
        self.assertEquals(num_cats, 1)
