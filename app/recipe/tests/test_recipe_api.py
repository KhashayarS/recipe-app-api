from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Ingredient, Tag

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPE_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Return recipe detail url"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_ingredient(user, name='Main course'):
    return Ingredient.objects.create(user=user, name=name)


def sample_tag(user, name='cinnamon'):
    return Tag.objects.create(user=user, name=name)


def sample_recipe(user, **params):
    """Create and return a sample recipe"""
    defaults = {
        'title': 'Sample Recipe',
        'time_minutes': 26,
        'price': 5.00
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTests(TestCase):
    """Test how recipe is publicly accessable"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test the accessibility of authorized users"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@gmail.com',
            'test123'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """test that authorized user has access to recipe"""
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_access_limited_to_authorized_user(self):
        "Test that authorization is necessary for posting recipes"
        user2 = get_user_model().objects.create_user(
            'other@gmail.com',
            'test2'
        )
        sample_recipe(user=user2)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        # print("====> ", res)
        # print("====> ", res.data)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        """Test retrieving a detailed list"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_base_recipe(self):
        """Test if a base recipe can be created successfully"""
        payload = {
            'title': 'pizza',
            'time_minutes': 25,
            'price': 3.00
        }
        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """Test if creating recipe with tag is available"""
        tag1 = sample_tag(user=self.user, name='Main Course')
        tag2 = sample_tag(user=self.user, name='Vegan')
        payload = {
            'title': 'Sample Recipe',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 25,
            'price': 3.45
        }
        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """Test that creating recipes with ingredients is avaiable"""
        ingredient1 = sample_ingredient(user=self.user, name='Salt')
        ingredient2 = sample_ingredient(user=self.user, name='Eggs')
        payload = {
            'title': 'Omlet',
            'ingredients': [ingredient1.id, ingredient2.id],
            'time_minutes': 10,
            'price': 1.00
        }
        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_partial_update_recipe(self):
        """Test if recipe updates successfully"""
        recipe = sample_recipe(user=self.user)
        tag = sample_tag(user=self.user)
        recipe.tags.add(tag)
        new_tag = sample_tag(user=self.user, name='dessert')

        payload = {
            'title': 'Cheesecake',
            'tags': [new_tag.id]
        }
        url = detail_url(recipe.id)
        self.client.patch(url, payload)
        # print('----->>>>', (res.status_code == status.HTTP_200_OK))

        recipe.refresh_from_db()
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_recipe(self):
        """Test update entire recipe using get request"""
        recipe = sample_recipe(user=self.user)
        tag = sample_tag(user=self.user)
        recipe.tags.add(tag)
        payload = {
            'title': 'Pizza',
            'time_minutes': 20,
            'price': 4.00
        }
        url = detail_url(recipe.id)
        self.client.put(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        self.assertEqual(recipe.price, payload['price'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 0)
