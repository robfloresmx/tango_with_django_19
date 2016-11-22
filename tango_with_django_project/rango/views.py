from django.shortcuts import render
# Import Category Model
from rango.models import Category


# Create your views here.

def index(request):
    # Query the database for a list of ALL categories currently stored
    # Order the categories by no. likes in descending order.
    # Retrieve the top 5 only - or all if less than 5.
    # Place the list in a context dictionary.
    # that will be passed to the template engine

    category_list = Category.objects.order_by('-likes')[:5]
    context_dict = {'categories': category_list}

    # In the '-likes' parameter, the '-' stands for descending
    # [:5] splits the list and takes the elements from 0 to 4

    # Return the reponse and send it back!
    return render(request, 'rango/index.html', context=context_dict)
