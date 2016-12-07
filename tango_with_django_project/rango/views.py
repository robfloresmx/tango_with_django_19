from django.shortcuts import render
from rango.models import Category, Page
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from datetime import datetime
import requests


# Create your views here.

def index(request):
    # Query the database for a list of ALL categories currently stored
    # Order the categories by no. likes in descending order.
    # Retrieve the top 5 only - or all if less than 5.
    # Place the list in a context dictionary.
    # that will be passed to the template engine

    # In the '-likes' parameter, the '-' stands for descending
    # [:5] splits the list and takes the elements from 0 to 4

    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = {'categories': category_list, 'pages': page_list}

    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']

    # Test : print client_id
    print(str(request.session['client_id']))

    # Obtain our Response object early so we can add cookie information
    response = render(request, 'rango/index.html', context_dict)

    # Return the reponse and send it back!
    return response


def about(request):
    return render(request, 'rango/about.html', {})


def show_category(request, category_name_slug):
    # Create a context dictionary whidh we can pass
    # to the template rendering engine
    context_dict = {}

    try:
        # Can we find a category name slug with the given name?
        # If we can't, the .get() method raises a DoesNotExist exception
        # So the .get() method returns one model instance or raises an exception.
        category = Category.objects.get(slug=category_name_slug)

        # Retrieve all of the associated pages.
        # Note that filter() will return a list of page objects or an empty list
        pages = Page.objects.filter(category=category)

        # Adds our results list to the template context under name pages.
        context_dict['pages'] = pages
        # We also add the category object from
        # the database dictionary.
        # We'll use this in the template to verify that the category exists
        context_dict['category'] = category
    except Category.DoesNotExist:

        # We get here if we didn't find the specified category.
        # Don't do anything - the template will display the "no category message" for us.
        context_dict['category'] = None
        context_dict['pages'] = None

    return render(request, 'rango/category.html', context_dict)


def add_category(request):
    form = CategoryForm()

    # AN HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database.
            form.save(commit=True)
            # Now that the category is saved
            # We could give a confirmation message
            # But since the most recent category added is on the index page
            # Then we can direct the user back to the index page.
            return index(request)
        else:
            # The supplied form contained errors -
            # just print them to the terminal
            print(form.errors)

    return render(request, 'rango/add_category.html', {'form': form})


def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    form = PageForm()
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                return show_category(request, category_name_slug)
        else:
            print(form.errors)

    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context_dict)


def register(request):
    # A boolean value for telling the template
    # whether the registration was successful.
    # Set to False initially. Code changes value to
    # True when registration succeeds.
    registered = False

    # if it's a HTTP POST, we're interested in processing data
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        # If the two forms are valid ...
        if user_form.is_valid() and profile_form.is_valid():
            # Save the user's form data to the database
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object
            user.set_password(user.set_password)
            user.save()

            # now sort out the UserProfile instance.
            # Since we need to set the user attribute ourselves,
            # we set commit=False. This delays saving the model
            # until we're ready to avoid integrity problems
            profile = profile_form.save(commit=False)
            profile.user = user

            # Did the user provide a profile picture?
            # If so, we need to get it from the input form and
            # put it in the UserProfile model

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # Now we save the UserProfile model instance
            profile.save()

            # Update our variable to indicate that the template
            # registration was successful
            registered = True

        else:
            # Invalid form or forms - mistakes or something else?
            # Print problems to the terminal
            print(user_form.errors, profile_form.errors)

    else:
        # Not a HTTP POST, so we render our form using two ModelForm instances.
        #  These forms will be blank, ready for user input.
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request, 'rango/register.html',
                  {'user_form': user_form,
                   'profile_form': profile_form,
                   'registered': registered})


#   USER_LOGIN VIEW
def user_login(request):
    # If the request is a POST request, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        # We use request.POST.get('<variable>') as opposed
        # to request.POST['<variable>'], because the
        # request.POST.get('<variable>') returns None if the
        # value doesn't exist, while request.POST['<variable>']
        # will raise a KeyError exception.
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of value), no user
        # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                # An inactive user account was used - no logging in!
                return HttpResponse("Your Rango account is disabled.")
        else:
            # Bad Login details were provided. So we can't log the user in.
            print("Invaled login details: {0}, {1}".format(username, password))
            return HttpResponse("Invalid login details supplied.")

            # The request is not a POST, display the login form.
            # This scenario would most likely be an HTTP GET
    else:
        # No context variable to pass to the template system, hence a blank dictionary
        return render(request, 'rango/login.html', {})


# LOG OUT VIEW
# Use the login_required decorator to ensure that only logged in users and log out
@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)
    # Take the user back to the homepage
    return HttpResponseRedirect(reverse('index'))


# RESTRICTED VIEW
# This annotation is a Django decorator
@login_required
def restricted(request):
    return HttpResponse("Since you're logged in, you can see this text")


# HELPER FUNCTIONS
def visitor_cookie_handler(request):
    # Get the number of visits to the site.
    # We use the COOKIES.get() function to obtain the visits cookie.
    # If the cookie exists, the value returned is casted to an integer.
    # If the cookie doesn't exist, then the default value of 1 is used
    visits = int(request.COOKIES.get('visits', '1'))

    last_visit_cookie = request.COOKIES.get('last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')

    # If it's been more than a day since the last visit ...
    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        # update the last visit cookie now that we have updated the count
        request.session['last_visit'] = str(datetime.now())
    else:
        visits = 1
        # set the last visit oookie
        request.session['last_visit'] = last_visit_cookie

    # Update/set the visits cookie
    request.session['visits'] = visits

    # Set the clientId cookie
    client_id_response = get_client_id()
    if client_id_response:
        request.session['client_id'] = client_id_response["id"]

    client_id = str(request.session['client_id'])

    extra_headers = {'X-Client-Id', client_id}
    auth_token_response = get_auth_token(extra_headers)
    if auth_token_response:
        request.session['authToken'] = auth_token_response["authToken"]


def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val


def get_client_id():
    url = "https://preprod.mobile.trycasa.com/v1/clients/client-ids"
    return send_request(url, {}, {})


def get_auth_token(extra_headers):
    url = "https://preprod.mobile.trycasa.com/v1/clients/auth-tokens"
    return send_request(url,
                        {}
                        , extra_headers)


def send_request(url, data, extra_headers):
    headers = get_headers()
    if extra_headers:
        headers.update(extra_headers)
    response = requests.post(url, verify=False, data=data, headers=headers)
    if response:
        response = response.json()
    return response


def get_headers():
    headers = {"X-Api-Username": "Api-Username",
               "X-Api-Password": "Api-Password",
               "X-Device-Id": "deviceId",
               "X-App-Version": "1.80",
               "organizationID": "",
               "projectID": "",
               "appID": ""}
    return headers
