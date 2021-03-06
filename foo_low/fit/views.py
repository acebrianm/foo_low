from django.shortcuts import render
from django.template import loader
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from .models import Tag, Profile, Event
from .forms import TagForm, TagAdminForm, EventForm
from datetime import datetime
from django.core.exceptions import PermissionDenied

# Index redirection in the website.
def index(request):
    if not request.user.is_authenticated:
        template = loader.get_template('fit/login.html')
        context ={}
        return HttpResponse(template.render(context, request))

    else:
        # Template render
        template = loader.get_template('fit/index.html')
        tag_list = Tag.objects.all().filter(is_active=True)
        context = {
            'tag_list': tag_list
        }
        return HttpResponse(template.render(context, request))

# Log in
def log_in(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(request, username=username, password=password)
    print(username)
    print(password)
    if user is not None:
        login(request, user)
        return index(request)
    else:
        messages.error(request, 'Wrong username or password.')
        return index(request)

# Log out
def log_out(request):
    logout(request)
    return index(request)

# Webpage to follow or unfollow interests.
def my_account(request):
    """
    Displays all the tags that are available and the ones
    that you have selected appear with a marked in the checkbox
    
    **Context**

    ``tags``
        All the active tags in the :model:`fit.Tag`.
    ``username``
        An instance of the :model:`auth.User`
    ``form``
        An instance of the TagForm

    **Template:**

    :template:`fit/list_tags.html`
    """
    # Data from tags
    tags = Tag.objects.all().filter(is_active=True)
    # Data from user
    current_user = request.user
    username = current_user.username
    current_profile = Profile.objects.get(user=current_user)

    if request.user.is_superuser:
        template = loader.get_template('fit/list_tags.html')
        form = {}
        
    else:
        # Template render
        template = loader.get_template('fit/my_account.html')
    
        # Create the form
        if request.method == 'POST':
            form = TagForm(request.POST or None,
                           request.FILES or None,
                           instance=current_profile,)
            if form.is_valid():
                form.save()
        
        else:
            form = TagForm(instance=current_profile)

    # Context for rendering
    context = {
        'tags' : tags,
        'username' : username,
        'form' : form,
    }

    # Render the webpage
    return HttpResponse(template.render(context, request))

# Add new tags
def add_tag(request):
    """
    Add a new entry of :model:`fit.Tag`.
    
    **Context**

    ``form``
        An instance of the TagAdminForm

    **Template:**

    :template:`fit/add_tag.html`
    """
    if not request.user.is_superuser:
        raise PermissionDenied
    # Template render
    template = loader.get_template('fit/add_tag.html')
    
    # Create the form
    if request.method == 'POST':
        form = TagAdminForm(request.POST or None,
                            request.FILES or None,)
        if form.is_valid():
            form.save()
            return my_account(request)
        
    else:
        form = TagAdminForm()

    # Context for rendering
    context = {
        'form' : form,
    }
    # Render the webpage
    return HttpResponse(template.render(context, request))

def list(request, tag=None):
    """
    Displays all the active events depending on the user, it is related with
    :model:`fit.Event` and  :model:`fit.Tag`.

    Superuser:
        - Displays all the events from all categories
        - Edit and Delete button appear at the bottom of each event
        - New Event button

    Normal User:
        - Displays all the events that are in the categories that the user is
          following

    Select Tag:
        - Displays all the events which have the selected tag
    
    **Context**

    ``tag_list``
        All tags that are active
    ``events``
        It is a zipped list with two list inside. The event list that have all
        the entries that meets the queries conditions. The image is a list of
        string that only contains the name of the image

    **Template:**

    :template:`fit/list.html`
    """

    if not request.user.is_authenticated:
        return index(request)

    tag_list = Tag.objects.all().filter(is_active=True)

    if request.user.is_superuser:
        if tag:
            events = Event.objects.filter(event_tag__tag_name=tag).distinct()
            events = events.filter(is_active=True)
        else:
            events = Event.objects.all().distinct()
            events = events.filter(is_active=True)
    else:
        if tag:
            events = Event.objects.filter(event_tag__tag_name=tag).filter(date__gte=datetime.now()).filter(is_active=True).distinct()
            events = events.filter(event_tag__is_active=True)
        else:
            user_tags = Profile.objects.get(id=request.user.id).profile_tag.all()
            events = Event.objects.filter(event_tag__in=user_tags).filter(is_active=True).filter(date__gte=datetime.now()).distinct() 
            events = events.filter(event_tag__is_active=True)
    images = []
    for event in events:
        images.append(event.image.name.split('/')[4])
        
    template = loader.get_template("fit/list.html")
    context = {
        'tag_list': tag_list, 
        'events' : zip(events, images)
    }
    return HttpResponse(template.render(context, request))


def detail_event(request, event=None):
    """
    Displays all the information from the selected event.
    
    **Context**

    ``tag_list``
        All tags that are active
    ``event``
        The entry of the selected event
    ``image``
        The name of the image in the current event

    **Template:**

    :template:`fit/detail.html`
    """
    tag_list = Tag.objects.all().filter(is_active=True)

    if not request.user.is_authenticated or not event:
        return index(request)

    ev = get_object_or_404(Event, id=event)
    template = loader.get_template("fit/detail.html")
    image = "fit/images/" + ev.image.name.split('/')[4]
    context = {
        'tag_list': tag_list, 
        'event' : ev,
        'image' : image
    }
    return HttpResponse(template.render(context, request))

def edit_tag(request, tag):
    """
    Displays all the information from the selected tag and the admin is able to
    edit the information inside.
    
    **Context**

    ``form``
        An instance of the TagAdminForm

    **Template:**

    :template:`fit/detail.html`
    """
    if not request.user.is_superuser:
        raise PermissionDenied
    obj = get_object_or_404(Tag, id=tag)
    # Template render
    template = loader.get_template('fit/add_tag.html')
    
    # Create the form
    if request.method == 'POST':
        form = TagAdminForm(request.POST or None,
                            request.FILES or None,
                            instance=obj)
        if form.is_valid():
            form.save()
            return my_account(request)
        
    else:
        form = TagAdminForm(instance=obj)

    # Context for rendering
    context = {
        'form' : form,
    }

    # Render the webpage
    return HttpResponse(template.render(context, request))

# Delete existing tags
def delete_tag(request, tag):
    """
    Does not display any view, just put the is_active state to False
    
    **Context**


    **Template:**

    """
    if not request.user.is_superuser:
        raise PermissionDenied
    obj = get_object_or_404(Tag, id=tag)
    try:
        obj.is_active = False
        obj.save()
    except:
        messages.error(request, 'There are values that are still referenced')
    return my_account(request)

def add_event(request):
    """
    Add a new entry of :model:`fit.Event`.
    
    **Context**

    ``form``
        An instance of the EventForm

    **Template:**

    :template:`fit/add_event.html`
    """

    if not request.user.is_superuser:
        raise PermissionDenied
    # Template render
    template = loader.get_template('fit/add_event.html')
    
    # Create the form
    if request.method == 'POST':
        form = EventForm(request.POST or None,
                         request.FILES or None,)
        if form.is_valid():
            form.save()
            return list(request)
        
    else:
        form = EventForm()

    # Context for rendering
    context = {
        'form' : form,
    }
    # Render the webpage
    return HttpResponse(template.render(context, request))

# Delete existing events
def delete_event(request, event):
    """
    Does not display any view, just put the is_active state to False
    
    **Context**


    **Template:**

    """
    if not request.user.is_superuser:
        raise PermissionDenied

    obj = get_object_or_404(Event, id=event)
    try:
        obj.is_active = False
        obj.save()
    except:
        messages.error(request, 'There are values that are still referenced')
    return list(request)

# Edit an event
def edit_event(request, event):
    """
    Displays all the information from the selected :model:`fit.Event` and the admin is able to
    edit the information inside.
    
    **Context**

    ``form``
        An instance of the EventForm

    **Template:**

    :template:`fit/add_event.html`
    """
    if not request.user.is_superuser:
        raise PermissionDenied

    template = loader.get_template('fit/add_event.html')
    obj = get_object_or_404(Event, id=event)
    # Template render
    
    # Create the form
    if request.method == 'POST':
        form = EventForm(request.POST or None,
                            request.FILES or None,
                            instance=obj)
        if form.is_valid():
            form.save()
            return index(request)
        
    else:
        form = EventForm(instance=obj)

    # Context for rendering
    context = {
        'form' : form,
    }

    # Render the webpage
    return HttpResponse(template.render(context, request))
