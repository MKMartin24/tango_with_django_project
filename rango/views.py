# Create your views here.

from datetime import datetime
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from rango.models import Category,Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm

def index(request):

    #Query the db for a list of ALL categories currently stored.
    #Order the categories by th number oflikes in descending order
    #Retrieve the top 5 only -- or all if less than 5 pages
    #Place the list in our Ontext_dict (with our boldmessage)
    #that will be passed to the template engine

    category_list = Category.objects.order_by('-likes')[:5]
    pages_list = Page.objects.order_by('-views')[:5]

    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    context_dict['pages'] = pages_list
    
    visitor_cookie_handler(request)

    response = render(request, 'rango/index.html', context=context_dict)
    return response

def about(request):
    context_dict = {'boldmessage': 'MKMartin24'}
    if request.session.test_cookie_worked():
        print("TEST COOKIE WORKED!")
        request.session.delete_test_cookie()
    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']
    return render(request, 'rango/about.html', context=context_dict)

def show_category(request, category_name_slug):
    #Create a context dictionary which we can pass
    #to the template rendering machine
    context_dict = {}

    try:
        #Can we find a category name slug with the given name?
        #If we can't, the .get() raises a DoesNotExist exception.
        #The .get() method returns on emodel instance or raises an exception
        category = Category.objects.get(slug = category_name_slug)

        #Retrieve all of associated pages.
        #The filter() will return a list of page objects or an empty list
        pages = Page.objects.filter(category=category)

        #Add our results list to the template context under name pages.
        context_dict['pages'] = pages
        #We also add the category object from hte database to the context_dictionary
        #We'll use this in the template to verify that the category exists
        context_dict['category'] = category
    except Category.DoesNotExist:
        #We get here if we didn't find the specified category.
        #Don't do anything -
        #the template will display the "no category" message for us.
        context_dict['category'] = None
        context_dict['pages'] = None
    
    #Go render the response and return it to the client.
    return render(request, 'rango/category.html', context=context_dict)

@login_required
def add_category(request):
    form = CategoryForm()

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return redirect("{% url 'rango:index' %v}")
        else:
            print(form.errors)
    
    return render(request, 'rango/add_category.html', context={'form': form})

@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None
    
    if category is None:
        return redirect('/rango/')

    form = PageForm()

    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            page = form.save(commit=False)
            page.category = category
            page.views = 0
            page.save()

            return redirect(reverse('rango:show_category',kwargs={'category_name_slug':category_name_slug}))
        else:
            print(form.errors)
        
    
    context_dict = {'form': form, 'category':category}
    return render(request, 'rango/add_page.html', context=context_dict)

def register(request):
    registered = False
    if request.method=='POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()

            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save()

            registered = True

        else:
            print(user_form.errors, profile_form.errors)

    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    
    return render(request, 'rango/register.html', context={'user_form':user_form, 'profile_form':profile_form, 'registered':registered})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username,password=password)

        if user:
            if user.is_active:
                login(request,user)
                return redirect(reverse('rango:index'))
            else:
                return HttpResponse("Your Rango account is disabled.")
        else:
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, 'rango/login.html')

@login_required
def restricted(request):
    return render(request, 'rango/restricted.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('rango:index'))

def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val

def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits', '1'))
    last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')

    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        request.session['last_visit'] = str(datetime.now())
    else:
        request.session['last_visit'] = last_visit_cookie
    request.session['visits'] = visits