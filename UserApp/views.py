from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import *
from .forms import *
from homeapp.models import tbl_user,tbl_login
from django.db.models import Q,Count,Prefetch
from django.http import HttpResponse

def property_form(request, id=None):
    property_obj = None
    
    if id:
        property_obj = get_object_or_404(tbl_property, id=id)
    
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=property_obj)
        images = request.FILES.getlist('images')
        
        if form.is_valid():
            # Check for images only for new property creation
            if not property_obj and len(images) == 0:
                form.add_error(None, "At least one image is required for new properties.")
            else:
                try:
                    prop = form.save(commit=False)
                    user_id = request.session.get('user_id')
                    if user_id:
                        prop.owner = tbl_user.objects.get(id=user_id)
                    prop.save()
                    
                    # Save multiple images
                    for img in images:
                        tbl_property_images.objects.create(
                            property=prop,
                            image=img
                        )
                    
                    messages.success(request, 'Property saved successfully!')
                    return redirect('property_list')
                    
                except Exception as e:
                    messages.error(request, f'Error saving property: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PropertyForm(instance=property_obj)
    
    return render(request, 'user_manage_property.html', {
        'form': form,
        'property': property_obj
    })

def property_list(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')  # Adjust this to your login URL
    
    user = tbl_user.objects.get(id=request.session['user_id'])
    properties = tbl_property.objects.filter(owner=user).prefetch_related('images')
    
    # Add unread message count for each property
    for property in properties:
        property.unread_count = property.get_unread_count_for_user(user)
    return render(request, 'user_property_list.html', {'properties': properties})

def delete_property(request, id):
    prop = get_object_or_404(tbl_property, id=id)
    prop.delete()
    messages.success(request, 'Property deleted successfully!')
    return redirect('property_list')

def delete_property_image(request, id):
    img = get_object_or_404(tbl_property_images, id=id)
    property_id = img.property.id
    img.delete()
    messages.success(request, 'Image removed successfully!')
    return redirect('edit_property', id=property_id)


from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import json
from .models import tbl_property, tbl_property_images
from .forms import PropertyForm, PropertyImageForm

def add_images(request, property_id):
    property_obj = get_object_or_404(tbl_property, id=property_id)
    
    # Check if it's an AJAX request for the modal content
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method == 'GET':
            # Return HTML for the modal
            from django.template.loader import render_to_string
            html = render_to_string('add_property_images_modal.html', {
                'property': property_obj
            }, request=request)
            return JsonResponse({'html': html})
        
        elif request.method == 'POST':
            # Handle image upload
            images = request.FILES.getlist('images')  # Changed from 'images[]' to 'images'
            
            if not images:
                return JsonResponse({
                    'success': False,
                    'error': 'No images received'
                })
            
            uploaded_images = []
            for img in images:
                pi = tbl_property_images.objects.create(
                    property=property_obj,
                    image=img
                )
                uploaded_images.append({
                    'id': pi.id,
                    'url': pi.image.url,
                    'filename': pi.image.name.split('/')[-1]
                })
            
            return JsonResponse({
                'success': True,
                'message': f'{len(uploaded_images)} image(s) uploaded successfully!',
                'images': uploaded_images
            })
    
    # Regular request - redirect or render normally
    return redirect('view_property')  # or wherever you want



def add_property_images(request, property_id):
    property_obj = get_object_or_404(tbl_property, id=property_id)

    if request.method == 'POST':
        form = PropertyImageForm(request.POST, request.FILES)
        if form.is_valid():
            images = request.FILES.getlist('image')  # getlist for multiple files
            for img in images:
                tbl_property_images.objects.create(property=property_obj, image=img)
            messages.success(request, f'{len(images)} image(s) added successfully!')
            return redirect('edit_property', id=property_obj.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PropertyImageForm()

    return render(request, 'add_property_images.html', {
        'form': form,
        'property': property_obj
    })


################plot management###############

def plot_manage(request, plot_id=None):
     # Redirect to my_plots which lists all plots and has add/edit options
    if request.method == 'POST':
        if plot_id:  # Edit existing plot
            plot = get_object_or_404(tbl_plot_for_sale, id=plot_id, owner=request.session.get('user_id'))
            plot.title = request.POST.get('title')
            plot.address = request.POST.get('address')
            plot.area = request.POST.get('area')
            plot.price = request.POST.get('price')
            plot.plot_type = request.POST.get('plot_type')
            plot.description = request.POST.get('description')
            plot.availability_status = request.POST.get('availability_status')
            plot.water = request.POST.get('water') == 'true'
            plot.electricity = request.POST.get('electricity') == 'true'
            plot.gated_community = request.POST.get('gated_community') == 'true'
            plot.save()
            messages.success(request, 'Plot updated successfully!')
        else:  # Add new plot
            plot = tbl_plot_for_sale.objects.create(
                owner_id=request.session.get('user_id'),
                title=request.POST.get('title'),
                address=request.POST.get('address'),
                area=request.POST.get('area'),
                price=request.POST.get('price'),
                plot_type=request.POST.get('plot_type'),
                description=request.POST.get('description'),
                water=request.POST.get('water') == 'true',
                electricity=request.POST.get('electricity') == 'true',
                gated_community=request.POST.get('gated_community') == 'true'
            )
            messages.success(request, 'Plot added successfully!')
        
        # Handle image uploads
        images = request.FILES.getlist('images')
        for img in images:
            tbl_plot_images.objects.create(plot=plot, image=img)
        
        return redirect('my_plots')

    return redirect('my_plots')

def plot_delete(request, plot_id):
    plot = get_object_or_404(tbl_plot_for_sale, id=plot_id, owner=request.session.get('user_id'))
    plot.delete()
    messages.success(request, 'Plot deleted successfully!')
    return redirect('my_plots')

def plot_add_images(request):
    if request.method == 'POST':
        plot_id = request.POST.get('plot_id')
        plot = get_object_or_404(tbl_plot_for_sale, id=plot_id, owner=request.session.get('user_id'))
        
        images = request.FILES.getlist('images')
        for img in images:
            tbl_plot_images.objects.create(plot=plot, image=img)
        
        messages.success(request, f'{len(images)} image(s) added successfully!')
    return redirect('my_plots')

def plot_interest_respond(request):
    if request.method == 'POST':
        interest_id = request.POST.get('interest_id')
        status = request.POST.get('status')
        message = request.POST.get('response_message', '')
        
        interest = get_object_or_404(tbl_plot_interest, id=interest_id, plot__owner=request.session.get('user_id'))
        interest.status = status
        interest.response_message = message
        interest.save()
        
        # Create chat room if status is 'contacted'
       
        
        messages.success(request, f'Response sent successfully!')
    return redirect('my_plots')

def toggle_plot_wishlist(request, plot_id):
    if request.method == 'POST':
        plot = get_object_or_404(tbl_plot_for_sale, id=plot_id)
        wishlist_item = tbl_plot_wishlist.objects.filter(plot=plot, user=request.user)
        
        if wishlist_item.exists():
            wishlist_item.delete()
            return JsonResponse({'status': 'removed'})
        else:
            tbl_plot_wishlist.objects.create(plot=plot, user=request.user)
            return JsonResponse({'status': 'added'})
    return JsonResponse({'error': 'Invalid request'}, status=400)

def send_message_to_user(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        plot_id = request.POST.get('plot_id')
        message = request.POST.get('message')
        
        receiver = get_object_or_404(tbl_user, id=user_id)
        plot = get_object_or_404(tbl_plot_for_sale, id=plot_id, owner=request.session.get('user_id'))
        
        # Find the interest record and update it with the response
        interest = tbl_plot_interest.objects.filter(
            plot=plot,
            user=receiver
        ).first()
        
        if interest:
            interest.response_message = message
            interest.save()
            messages.success(request, f'Response sent to {receiver.name}!')
        else:
            messages.error(request, 'No interest record found for this user and plot.')
        
    return redirect('my_plots')

def my_plots(request):
    user_id = request.session.get('user_id')
    
    # Get all plots for this user with related data
    plots = tbl_plot_for_sale.objects.filter(
        owner_id=user_id
    ).prefetch_related(
        'images',
        Prefetch(
            'tbl_plot_interest_set',
            queryset=tbl_plot_interest.objects.select_related('user'),
            to_attr='interest_requests'
        )
    ).annotate(
        interest_count=Count('tbl_plot_interest'),
        pending_interest_count=Count('tbl_plot_interest', 
            filter=Q(tbl_plot_interest__status='pending')),
        contacted_interest_count=Count('tbl_plot_interest',
            filter=Q(tbl_plot_interest__status='contacted'))
    )
    
    # Get all interest requests for all plots (for the modal)
    all_interests = tbl_plot_interest.objects.filter(
        plot__owner_id=user_id
    ).select_related(
        'user', 'plot'
    ).order_by('-created_at')
    
    # Calculate total pending interests
    total_pending_interests = all_interests.filter(status='pending').count()
    
    # Check wishlist status for each plot
    for plot in plots:
        plot.is_wishlisted = tbl_plot_wishlist.objects.filter(
            plot=plot,
            user_id=user_id
        ).exists()
        
        # Add interest requests to plot object for easy access
        if hasattr(plot, 'interest_requests'):
            plot.interest_list = plot.interest_requests
        else:
            plot.interest_list = []
    
    # Plot type choices for the form
    plot_type_choices = tbl_plot_for_sale.PLOT_TYPE_CHOICES
    
    context = {
        'plots': plots,
        'all_interests': all_interests,
        'total_pending_interests': total_pending_interests,
        'plot_type_choices': plot_type_choices,
    }
    
    return render(request, 'user_manage_plot.html', context)


###########browse property##################
def browse_property(request):
    current_user = tbl_user.objects.get(id=request.session['user_id'])
    
    # Get all unique locations for dropdown
    property_locations = tbl_property.objects.exclude(owner=current_user).values_list('location', flat=True).distinct()
    plot_locations = tbl_plot_for_sale.objects.exclude(owner=current_user).values_list('address', flat=True).distinct()
    
    # Combine and get unique locations
    all_locations = list(set(list(property_locations) + list(plot_locations)))
    all_locations = [loc for loc in all_locations if loc]  # Remove None/empty values
    all_locations.sort()
    
    # Get all categories for home type filter (from tbl_property)
    home_types = tbl_category.objects.all()
    
    # Get filters from request
    property_type = request.GET.get('property_type', '')
    location = request.GET.get('location', '')
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')
    
    # Initialize querysets
    properties = tbl_property.objects.exclude(owner=current_user)
    plots = tbl_plot_for_sale.objects.exclude(owner=current_user)
    
    # Common filters for both
    if location:
        properties = properties.filter(location__icontains=location)
        plots = plots.filter(address__icontains=location)
    
    if price_min:
        properties = properties.filter(rent_amount__gte=price_min)
        plots = plots.filter(price__gte=price_min)
    
    if price_max:
        properties = properties.filter(rent_amount__lte=price_max)
        plots = plots.filter(price__lte=price_max)
    
    # Rent-specific filters
    if property_type != 'sale':  # Apply rent filters unless specifically viewing sale
        bedrooms = request.GET.get('bedrooms', '')
        bathrooms = request.GET.get('bathrooms', '')
        home_type = request.GET.get('home_type', '')
        furnishing = request.GET.get('furnishing', '')
        size_min = request.GET.get('size_min', '')
        size_max = request.GET.get('size_max', '')
        
        if bedrooms:
            properties = properties.filter(bedrooms=bedrooms)
        if bathrooms:
            properties = properties.filter(bathrooms=bathrooms)
        if home_type:
            properties = properties.filter(home_type_id=home_type)
        if furnishing:
            properties = properties.filter(furnishing=furnishing)
        if size_min:
            properties = properties.filter(size_sqft__gte=size_min)
        if size_max:
            properties = properties.filter(size_sqft__lte=size_max)
    
    # Sale-specific filters
    if property_type != 'rent':  # Apply sale filters unless specifically viewing rent
        plot_type = request.GET.get('plot_type', '')
        area_min = request.GET.get('area_min', '')
        area_max = request.GET.get('area_max', '')
        water = request.GET.get('water', '')
        electricity = request.GET.get('electricity', '')
        gated = request.GET.get('gated', '')
        
        if plot_type:
            plots = plots.filter(plot_type=plot_type)
        if area_min:
            plots = plots.filter(area__gte=area_min)
        if area_max:
            plots = plots.filter(area__lte=area_max)
        if water == 'true':
            plots = plots.filter(water=True)
        if electricity == 'true':
            plots = plots.filter(electricity=True)
        if gated == 'true':
            plots = plots.filter(gated_community=True)
    
    # Filter by property type if specified
    if property_type == 'rent':
        plots = plots.none()  # Empty queryset for plots
    elif property_type == 'sale':
        properties = properties.none()  # Empty queryset for properties
    
    # Get all plot types for filter dropdown
    plot_type_choices = dict(tbl_plot_for_sale.PLOT_TYPE_CHOICES)
    plot_types = [(key, value) for key, value in plot_type_choices.items()]
    
    # Get all furnishing types for filter dropdown
    furnishing_choices = dict(tbl_property.FURNISHING_CHOICES)
    furnishing_types = [(key, value) for key, value in furnishing_choices.items()]
    
    context = {
        'properties': properties,
        'plots': plots,
        'locations': all_locations,
        'home_types': home_types,
        'plot_types': plot_types,
        'furnishing_types': furnishing_types,
        'property_type': property_type,
    }
    return render(request, 'browse_property.html', context)



def property_detail(request, property_id):
    # Get the property or return 404
    property = get_object_or_404(tbl_property, id=property_id)
    
    # Get all images for this property
    images = property.images.all()
    
    context = {
        'property': property,
        'images': images,
    }
    
    return render(request, 'property_detail.html', context)



###########plot detail

def plot_detail(request, plot_id):
    # Get the property or return 404
    plot = get_object_or_404(tbl_plot_for_sale, id=plot_id)
    
    # Get all images for this property
    images = plot.images.all()
    
    context = {
        'plot': plot,
        'images': images,
    }
    
    return render(request, 'plot_detail.html', context)

#################chat #############

def chat_page(request, property_id, user_id):
    current_user = tbl_user.objects.get(id=request.session['user_id'])
    other_user = get_object_or_404(tbl_user, id=user_id)
    property_obj = get_object_or_404(tbl_property, id=property_id)

    # Check if room exists for this property
    room = tbl_chat_room.objects.filter(
        (
            Q(user1=current_user, user2=other_user) |
            Q(user1=other_user, user2=current_user)
        ),
        property=property_obj
    ).first()

    if not room:
        room = tbl_chat_room.objects.create(
            user1=current_user,
            user2=other_user,
            property=property_obj
        )

    return render(request, 'chat.html', {
        'room': room,
        'other_user': other_user,
        'property': property_obj
    })

def send_message(request):
    if request.method == "POST":
        room_id = request.POST.get('room_id')
        message = request.POST.get('message')

        room = tbl_chat_room.objects.get(id=room_id)
        sender = tbl_user.objects.get(id=request.session['user_id'])

        tbl_chat_message.objects.create(
            chat_room=room,
            sender=sender,
            message=message
        )

        return JsonResponse({'status': 'ok'})


def get_messages(request, room_id):
    room = get_object_or_404(tbl_chat_room, id=room_id)
    messages = room.messages.all().order_by('timestamp')

    data = []
    for msg in messages:
        data.append({
            'sender': msg.sender.name,
            'sender_id': msg.sender.id,  # CRITICAL: Add this!
            'message': msg.message,
            'time': msg.timestamp.strftime("%I:%M %p"),  # Better time format
            'date': msg.timestamp.strftime("%Y-%m-%d"),
        })

    return JsonResponse(data, safe=False)


from django.db.models import Q, OuterRef, Subquery, Count, Max
from django.utils import timezone

def property_chat_list(request, property_id):
    current_user = tbl_user.objects.get(id=request.session['user_id'])

    property_obj = get_object_or_404(
        tbl_property,
        id=property_id,
        owner=current_user
    )

    # Get all chat rooms for this property
    rooms = tbl_chat_room.objects.filter(property=property_obj).order_by('-updated_at')

    # 🔥 Attach customer manually and get last message info
    room_list = []
    for room in rooms:
        # Determine customer (the other user)
        if room.user1 == current_user:
            customer = room.user2
        else:
            customer = room.user1

        # Get last message for this room
        last_message = room.messages.order_by('-timestamp').first()
        
        # Count unread messages (messages not sent by current user and not read)
        unread_count = room.messages.filter(
            ~Q(sender=current_user),  # Not sent by current user
            is_read=False
        ).count()

        room_list.append({
            'room': room,
            'customer': customer,
            'last_message': last_message.message if last_message else None,
            'last_message_time': last_message.timestamp if last_message else None,
            'last_message_sender': last_message.sender if last_message else None,
            'unread_count': unread_count,
            'is_online': customer.is_online if hasattr(customer, 'is_online') else False,  # If you have online tracking
        })

    # Sort rooms by last message time (most recent first)
    room_list.sort(
        key=lambda x: x['last_message_time'] or timezone.datetime.min, 
        reverse=True
    )

    # Get total unread count across all rooms
    total_unread = sum(item['unread_count'] for item in room_list)

    context = {
        "room_list": room_list,
        "property": property_obj,
        "total_unread": total_unread,
        "total_enquiries": len(room_list)
    }

    return render(request, "property_chat_list.html", context)

def owner_chat_room(request, room_id):
    current_user = tbl_user.objects.get(id=request.session['user_id'])

    room = get_object_or_404(
        tbl_chat_room,
        id=room_id
    )

    # 🔥 security check: must be part of this room
    if current_user != room.user1 and current_user != room.user2:
        return HttpResponse("Not allowed")

    # find the other user
    if current_user == room.user1:
        other_user = room.user2
    else:
        other_user = room.user1

    return render(request, "chat.html", {
        "room": room,
        "other_user": other_user
    })


def interest_request_plot(request, id):
    plot = get_object_or_404(tbl_plot_for_sale, id=id)
    user = tbl_user.objects.get(id=request.session['user_id'])

    # Check if already interested
    if not tbl_plot_interest.objects.filter(plot=plot, user=user).exists():
        tbl_plot_interest.objects.create(plot=plot, user=user)

    return redirect('browse_property')  # change to your page name


def wishlist_plot(request, id):
    plot = get_object_or_404(tbl_plot_for_sale, id=id)
    user = tbl_user.objects.get(id=request.session['user_id'])

    # Toggle wishlist (add/remove)
    wishlist_item = tbl_plot_wishlist.objects.filter(plot=plot, user=user)

    if wishlist_item.exists():
        wishlist_item.delete()
    else:
        tbl_plot_wishlist.objects.create(plot=plot, user=user)

    return redirect('browse_property') 
 # change to your page name
def profile_view(request):
    """Main profile page with tabs"""
    # Get user from session
    try:
        user = tbl_user.objects.get(id=request.session.get('user_id'))
    except (tbl_user.DoesNotExist, KeyError):
        return redirect('login')
    
    active_tab = request.GET.get('tab', 'edit_profile')
    
    context = {
        'active_tab': active_tab,
        'user': user
    }
    
    # Load data based on active tab
    if active_tab == 'wishlist':
        # ADDED CONDITION: exclude(plot__owner=user)
        wishlist_items = tbl_plot_wishlist.objects.filter(
            user=user
        ).exclude(
            plot__owner=user  # Don't show plots owned by the logged-in user
        ).select_related('plot').prefetch_related('plot__images')
        
        # Add first image URL to each plot
        for item in wishlist_items:
            first_image = item.plot.images.first()
            item.plot.first_image_url = first_image.image.url if first_image else '/static/images/no-image.jpg'
        
        context['wishlist_items'] = wishlist_items
        
    elif active_tab == 'interested_plots':
        # ADDED CONDITION: exclude(plot__owner=user)
        interested_items = tbl_plot_interest.objects.filter(
            user=user
        ).exclude(
            plot__owner=user  # Don't show plots owned by the logged-in user
        ).select_related('plot').prefetch_related('plot__images')
        
        for item in interested_items:
            first_image = item.plot.images.first()
            item.plot.first_image_url = first_image.image.url if first_image else '/static/images/no-image.jpg'
        
        context['interested_items'] = interested_items
        
    elif active_tab == 'interested_rent_properties':
        # Get properties where user has initiated chat (rental properties)
        # Assuming chat rooms are created for rental property inquiries
        
        # Get all chat rooms where user is participant and property exists
        chat_rooms = tbl_chat_room.objects.filter(
            Q(user1=user) | Q(user2=user)
        ).filter(
            property__isnull=False  # Only rooms with properties
        ).select_related(
            'property', 'property__owner'
        ).prefetch_related(
            'property__images'
        ).order_by('-updated_at')
        
        # Create a list to avoid duplicate properties
        property_ids = set()
        interested_properties = []
        
        for room in chat_rooms:
            property = room.property
            # ADDED CONDITION: Skip if the current user is the owner of the property
            if property.owner == user:
                continue

            if property.id not in property_ids:
                property_ids.add(property.id)
                
                # Get first image
                first_image = property.images.first()
                
                # Create a custom object similar to interested_items structure
                class PropertyInterestWrapper:
                    def __init__(self, property, chat_room):
                        self.plot = property  # Keep as 'plot' for template compatibility
                        self.chat_room = chat_room
                        self.message = f"Last message: {room.messages.last().message[:50]}..." if room.messages.exists() else "Chat started"
                        self.created_at = room.created_at
                
                wrapper = PropertyInterestWrapper(property, room)
                wrapper.plot.first_image_url = first_image.image.url if first_image else '/static/images/no-image.jpg'
                interested_properties.append(wrapper)
        
        context['interested_properties'] = interested_properties
    
    return render(request, 'user_profile.html', context)

def update_profile(request):
    """Handle profile update via AJAX"""
    if request.method == 'POST':
        user=get_object_or_404(tbl_user,id=request.session['user_id'])
        
        # Update user fields
        user.name = request.POST.get('name', user.name)
        user.login.email = request.POST.get('email', user.login.email)
        user.phone = request.POST.get('phone', user.phone)
        # user.address = request.POST.get('address', user.address)
        
        # Handle profile picture upload
        if 'profile_pic' in request.FILES:
            user.profile_pic = request.FILES['profile_pic']
        
        user.save()
        messages.success(request, 'Profile updated successfully!')
        
        # return redirect(f'{request.META.get("HTTP_REFERER", "/profile/")}?tab=edit_profile')
    
    return redirect('profile')


def change_password(request):
    """Handle password change"""
    user=get_object_or_404(tbl_user,id=request.session['user_id'])
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Verify current password
        if (current_password!= user.login.password):
            messages.error(request, 'Current password is incorrect!')
            return redirect(f'{request.META.get("HTTP_REFERER", "/profile/")}?tab=change_password')
        
        # Check if new passwords match
        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match!')
            return redirect(f'{request.META.get("HTTP_REFERER", "/profile/")}?tab=change_password')
        
        # Check password length
        if len(new_password) < 6:
            messages.error(request, 'Password must be at least 6 characters long!')
            return redirect(f'{request.META.get("HTTP_REFERER", "/profile/")}?tab=change_password')
        
        # Update password
        
        login=get_object_or_404(tbl_login,id=user.login_id)
        login.password=new_password
        login.save()

        
        messages.success(request, 'Password changed successfully! Please login again.')
        return redirect('login')  # Redirect to login page
    
    return redirect('profile')

def wishlist_view(request):
    """View wishlist items"""
    try:
        user = tbl_user.objects.get(id=request.session.get('user_id'))
    except (tbl_user.DoesNotExist, KeyError):
        return redirect('login')  # or handle appropriately
    
    # Get wishlist items with related data
    wishlist_items = tbl_plot_wishlist.objects.filter(
        user=user
    ).select_related('plot').prefetch_related('plot__images')
    
    # Add image URL to each plot
    for item in wishlist_items:
        first_image = item.plot.images.first()
        item.plot.image_url = first_image.image.url if first_image else '/static/images/no-image.jpg'
    
    return render(request, 'wishlist_partial.html', {'wishlist_items': wishlist_items})


def interested_plots_view(request):
    """View interested plots"""
    try:
        user = tbl_user.objects.get(id=request.session.get('user_id'))
    except (tbl_user.DoesNotExist, KeyError):
        return redirect('login')  # or handle appropriately
    
    # Get interested items with related data
    interested_items = tbl_plot_interest.objects.filter(
        user=user
    ).select_related('plot').prefetch_related('plot__images')
    
    # Add image URL to each plot
    for item in interested_items:
        first_image = item.plot.images.first()
        item.plot.image_url = first_image.image.url if first_image else '/static/images/no-image.jpg'
    
    return render(request, 'interested_plots_partial.html', {'interested_items': interested_items})
def remove_from_wishlist(request, plot_id):
    """Remove plot from wishlist"""
    user=get_object_or_404(tbl_user,id=request.session['user_id'])
    wishlist_item = get_object_or_404(tbl_plot_wishlist, plot_id=plot_id, user=user)
    wishlist_item.delete()
    messages.success(request, 'Removed from wishlist!')
    return redirect('profile')


def remove_interest(request, interest_id):
    """Remove plot interest"""
    user=get_object_or_404(tbl_user,id=request.session['user_id'])
    interest_item = get_object_or_404(tbl_plot_interest, id=interest_id, user=user)
    interest_item.delete()
    messages.success(request, 'Interest removed!')
    return redirect('profile')


def interested_rent_properties(request):
    """View properties where user has initiated chat (as either user1 or user2)"""
    try:
        user = tbl_user.objects.get(id=request.session.get('user_id'))
    except (tbl_user.DoesNotExist, KeyError):
        return redirect('login')
    
    # Get all chat rooms where user is either user1 or user2 and property exists
    chat_rooms = tbl_chat_room.objects.filter(
        Q(user1=user) | Q(user2=user)
    ).filter(
        property__isnull=False  # Only rooms with properties
    ).select_related(
        'property', 'property__owner', 'user1', 'user2'
    ).prefetch_related(
        'property__images', 'messages'
    ).order_by('-updated_at')  # Most recent chats first
    
    # Enhance each chat room with additional data
    default_image = '/static/images/no-image.jpg'
    interested_properties = []
    
    for room in chat_rooms:
        property = room.property
        
        # Determine the other user in the chat (not the current user)
        other_user = room.user2 if room.user1 == user else room.user1
        
        # Get last message in the chat
        last_message = room.messages.order_by('-timestamp').first()
        
        # Get unread count for current user
        unread_count = room.messages.filter(
            ~Q(sender=user),  # Messages not sent by current user
            is_read=False
        ).count()
        
        # Get first property image
        first_image = property.images.first()
        
        # Create a custom object with all needed data
        property_data = {
            'chat_room': room,
            'property': property,
            'other_user': other_user,
            'other_user_name': other_user.name,
            'other_user_phone': other_user.phone,
            'other_user_email': other_user.email,
            'last_message': last_message,
            'last_message_text': last_message.message if last_message else "No messages yet",
            'last_message_time': last_message.timestamp if last_message else room.created_at,
            'unread_count': unread_count,
            'first_image_url': first_image.image.url if first_image else default_image,
            'chat_started_at': room.created_at,
            'last_activity': room.updated_at,
            'total_messages': room.messages.count(),
            'is_owner': property.owner == user,  # Whether current user is the property owner
        }
        
        interested_properties.append(property_data)
    
    context = {
        'interested_properties': interested_properties,
        'total_chats': len(interested_properties),
        'unread_total': sum(item['unread_count'] for item in interested_properties)
    }
    print(context)
    
    return render(request, 'interested_properties.html', context)
def remove_rental_interest(request, property_id):
    """Remove rental property interest"""
    try:
        user = tbl_user.objects.get(id=request.session.get('user_id'))
        # You can add logic here to remove from tracking if needed
        messages.success(request, 'Property removed from your interested list')
    except Exception as e:
        messages.error(request, f'Error removing property: {str(e)}')
    
    return redirect('profile')

# ... existing imports ...

from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import tbl_feedback, tbl_user


def feedback_list(request):
    """Display list of feedback submitted by the user."""
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    try:
        user = tbl_user.objects.get(id=user_id)
    except tbl_user.DoesNotExist:
        return redirect('login')

    feedbacks = tbl_feedback.objects.filter(user=user)

    context = {
        'feedbacks': feedbacks,
    }
    return render(request, 'feedback_lista.html', context)


def submit_feedback(request):
    """Handle AJAX feedback submission."""
    if request.method == 'POST':
        user_id = request.session.get('user_id')

        if not user_id:
            return JsonResponse({
                'status': 'error',
                'message': 'User not logged in'
            }, status=401)

        try:
            user = tbl_user.objects.get(id=user_id)
        except tbl_user.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid user'
            }, status=404)

        subject = request.POST.get('subject')
        message = request.POST.get('message')
        feedback_type = request.POST.get('feedback_type', 'other')

        # Validation
        if not subject or not message:
            return JsonResponse({
                'status': 'error',
                'message': 'Subject and message are required.'
            })

        # Validate feedback_type
        valid_types = [choice[0] for choice in tbl_feedback.FEEDBACK_TYPE_CHOICES]
        if feedback_type not in valid_types:
            feedback_type = 'other'

        try:
            tbl_feedback.objects.create(
                user=user,
                subject=subject,
                message=message,
                feedback_type=feedback_type
            )

            return JsonResponse({
                'status': 'success',
                'message': 'Feedback submitted successfully!'
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request'
    }, status=400)