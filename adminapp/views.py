from django.shortcuts import render,redirect,get_object_or_404
from homeapp.models import tbl_login,tbl_user
from .models import *
from .forms import *
from UserApp.models import tbl_plot_for_sale,tbl_property,tbl_plot_interest
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone


# Create your views here.
def view_users(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        action = request.POST.get("action")

        user = tbl_user.objects.get(id=user_id)

        if action == "revoke":
            user.status = "Revoked"
        elif action == "restore":
            user.status = "Active"

        user.save()
        return redirect("view_users")

    users = tbl_user.objects.all()
    return render(request, "admin_manage_user.html", {"users": users})


#==============category management==================

def category_page(request, id=None):
    if id:
        category = get_object_or_404(tbl_category, id=id)
    else:
        category = None

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category_page')
    else:
        form = CategoryForm(instance=category)

    categories = tbl_category.objects.all()

    return render(request, 'admin_category_management.html', {
        'form': form,
        'categories': categories
    })


def delete_category(request, id):
    category = get_object_or_404(tbl_category, id=id)
    category.delete()
    return redirect('category_page')


def admin_reject_property(request, property_id):
    """Reject a property listing with reason"""
   
    if request.method == 'POST':
        property = get_object_or_404(tbl_property, id=property_id)
        reason = request.POST.get('rejection_reason', '').strip()
        
        if not reason:
            messages.error(request, 'Please provide a reason for rejection.')
            return redirect('admin_properties')
        
        # Update property status
        property.availability_status = 'rejected'
        # property.rejection_reason = reason
        # property.rejected_at = timezone.now()  # If you have this field
        # If you track who rejected
        property.save()
        
        # Optional: Send rejection notification to property owner
        # send_rejection_notification(property.owner.email, property.title, reason)
        
        messages.success(request, f'Property "{property.title}" has been rejected.')
        
        # Log the action
        # admin_log(request.session.get('admin_id'), 'REJECT_PROPERTY', property.id)
    
    return redirect('admin_properties')


# ... existing imports ...

def admin_plots(request):
    """View all plots with filtering and search"""
    
    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('search', '')
    
    # Base queryset
    # Optimization: select_related owner__login to avoid extra queries during search/display
    plots = tbl_plot_for_sale.objects.all().select_related(
        'owner', 'owner__login'
    ).prefetch_related(
        'images'
    ).order_by('-created_at')
    
    # Apply filters
    if status_filter != 'all':
        plots = plots.filter(availability_status=status_filter)
    
    # Apply search filter
    if search_query:
        plots = plots.filter(
            Q(title__icontains=search_query) |
            Q(address__icontains=search_query) |
            Q(owner__name__icontains=search_query) |
            # FIX: Changed owner__email to owner__login__email
            Q(owner__login__email__icontains=search_query)
        )
    
    # Get counts for dashboard
    total_plots = tbl_plot_for_sale.objects.count()
    available_count = tbl_plot_for_sale.objects.filter(availability_status='Available').count()
    sold_count = tbl_plot_for_sale.objects.filter(availability_status='Sold').count()
    reserved_count = tbl_plot_for_sale.objects.filter(availability_status='Reserved').count()
    
    context = {
        'plots': plots,
        'total_plots': total_plots,
        'available_count': available_count,
        'sold_count': sold_count,
        'reserved_count': reserved_count,
        'current_status': status_filter,
        'search_query': search_query,
    }
    
    return render(request, 'admin_plot_list.html', context)


def admin_reject_plot(request, plot_id):
    """Reject a plot listing with reason"""
    if request.method == 'POST':
        plot = get_object_or_404(tbl_plot_for_sale, id=plot_id)
        reason = request.POST.get('rejection_reason', '').strip()
        
        if not reason:
            messages.error(request, 'Please provide a reason for rejection.')
            return redirect('admin_plots')
            
        plot.availability_status = 'rejected'
        # Assuming you have a rejection_reason field on the model
        if hasattr(plot, 'rejection_reason'):
            plot.rejection_reason = reason
        plot.save()
        
        messages.success(request, f'Plot "{plot.title}" has been rejected.')
    
    return redirect('admin_plots')


def admin_restore_plot(request, plot_id):
    """Restore a rejected plot listing"""
    if request.method == 'POST':
        plot = get_object_or_404(tbl_plot_for_sale, id=plot_id)
        
        # Reset status to default
        plot.availability_status = 'Available'
        
        # Clear rejection data if fields exist
        if hasattr(plot, 'rejection_reason'):
            plot.rejection_reason = ''
            
        plot.save()
        
        messages.success(request, f'Plot "{plot.title}" has been restored successfully.')
    
    return redirect('admin_plots')

# ... rest of your views ...

def admin_properties(request):
    """View all properties with filtering and search"""
    
    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort', '-created_at')
    
    # Base queryset with related data
    # optimization: select_related 'owner__login' to prevent extra queries during search/display
    properties = tbl_property.objects.all().select_related(
        'owner', 'home_type', 'owner__login'
    ).prefetch_related(
        'images'
    ).order_by(sort_by)
    
    # Apply status filter
    if status_filter != 'all':
        properties = properties.filter(availability_status=status_filter)
    
    # Apply search filter
    if search_query:
        properties = properties.filter(
            Q(title__icontains=search_query) |
            Q(address__icontains=search_query) |
            Q(location__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(owner__name__icontains=search_query) |
            # FIX: Changed owner__email to owner__login__email
            Q(owner__login__email__icontains=search_query) |
            # Assuming phone is on the user model, otherwise adjust to owner__login__phone if needed
            Q(owner__phone__icontains=search_query) 
        )
    
    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(properties, 12)  # Show 12 properties per page
    
    try:
        properties_paginated = paginator.page(page)
    except PageNotAnInteger:
        properties_paginated = paginator.page(1)
    except EmptyPage:
        properties_paginated = paginator.page(paginator.num_pages)
    
    # Get counts for dashboard
    total_properties = tbl_property.objects.count()
    pending_count = tbl_property.objects.filter(availability_status='Avalable').count()
    approved_count = tbl_property.objects.filter(availability_status='Sold').count()
    rejected_count = tbl_property.objects.filter(availability_status='Reserved').count()
    
    # Get recent activity
    recent_approvals = tbl_property.objects.filter(
        admin_status='approved'
    ).order_by('-updated_at')[:5] if hasattr(tbl_property, 'updated_at') else []
    
    context = {
        'properties': properties_paginated,
        'total_properties': total_properties,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'recent_approvals': recent_approvals,
        'current_status': status_filter,
        'search_query': search_query,
        'sort_by': sort_by,
        'paginator': paginator,
    }
    
    return render(request, 'admin_property_list.html', context)


def admin_property_detail(request, property_id):
    """View detailed information about a specific property"""
   
    property = get_object_or_404(
        tbl_property.objects.select_related(
            'owner', 'home_type'
        ).prefetch_related(
            'images'
        ),
        id=property_id
    )
    
    # Get similar properties (same location or same category)
    similar_properties = tbl_property.objects.filter(
        Q(location__icontains=property.location) |
        Q(home_type=property.home_type)
    ).exclude(id=property_id)[:3]
    
    context = {
        'property': property,
        'similar_properties': similar_properties,
    }
    
    return render(request, 'admin_property_detail.html', context)




def admin_reject_plot(request, plot_id):
    """Simple reject plot function"""
    if request.method == 'POST':
        plot = get_object_or_404(tbl_plot_for_sale, id=plot_id)
        reason = request.POST.get('reason', '')
        print(reason)
        plot.availability_status = 'rejected'
        plot.rejection_reason = reason
        plot.save()
        
        messages.success(request, f'Plot "{plot.title}" rejected')
    

    return redirect('admin_plots')
    
    

def admin_plot_detail(request, plot_id):
    """View detailed information about a specific plot"""
    
    # Get the plot with related data (optimization)
    plot = get_object_or_404(
        tbl_plot_for_sale.objects.select_related(
            'owner', 'owner__login'
        ).prefetch_related(
            'images'
        ),
        id=plot_id
    )
    
    # Get similar plots (same location/address) excluding current one
    similar_plots = tbl_plot_for_sale.objects.filter(
        Q(address__icontains=plot.address) |
        Q(plot_type=plot.plot_type)
    ).exclude(id=plot.id)[:3]
    
    context = {
        'plot': plot,
        'similar_plots': similar_plots,
    }
    
    return render(request, 'admin_plot_detail.html', context)
    
  

from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta, datetime
from django.db.models.functions import TruncMonth, TruncDay

def admin_analytics(request):
    """Admin analytics dashboard with statistics and charts"""

    # Date range filter
    days = int(request.GET.get('days', 30))
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    # ========== PROPERTY STATISTICS ==========
    # Total properties
    total_properties = tbl_property.objects.count()
    
    # Properties by admin status
    pending_properties = tbl_property.objects.filter(availability_status='Available').count()
    approved_properties = tbl_property.objects.filter(availability_status='Available').count()
    rejected_properties = tbl_property.objects.filter(availability_status='Available').count()
    
    # Properties by availability
    available_properties = tbl_property.objects.filter(availability_status='Available').count()
    occupied_properties = tbl_property.objects.filter(availability_status='Occupied').count()
    maintenance_properties = tbl_property.objects.filter(availability_status='Maintenance').count()
    
    # Properties by furnishing type
    furnished_properties = tbl_property.objects.filter(furnishing='Furnished').count()
    semi_furnished = tbl_property.objects.filter(furnishing='Semi-Furnished').count()
    unfurnished_properties = tbl_property.objects.filter(furnishing='Unfurnished').count()
    
    # Properties by bedroom count
    properties_1bhk = tbl_property.objects.filter(bedrooms=1).count()
    properties_2bhk = tbl_property.objects.filter(bedrooms=2).count()
    properties_3bhk = tbl_property.objects.filter(bedrooms=3).count()
    properties_4plus = tbl_property.objects.filter(bedrooms__gte=4).count()
    
    # Properties by category
    properties_by_category = tbl_category.objects.annotate(
        count=Count('tbl_property')
    ).values('name', 'count')
    
    # Recent properties
    recent_properties = tbl_property.objects.select_related('owner').order_by('-created_at')[:10]
    
    # ========== PLOT STATISTICS ==========
    # Total plots
    total_plots = tbl_plot_for_sale.objects.count()
    
    # Plots by admin status
    pending_plots = tbl_plot_for_sale.objects.filter(availability_status='Available').count()
    approved_plots = tbl_plot_for_sale.objects.filter(availability_status='Available').count()
    rejected_plots = tbl_plot_for_sale.objects.filter(availability_status='Available').count()
    
    # Plots by availability
    available_plots = tbl_plot_for_sale.objects.filter(availability_status='Available').count()
    sold_plots = tbl_plot_for_sale.objects.filter(availability_status='Sold').count()
    reserved_plots = tbl_plot_for_sale.objects.filter(availability_status='Reserved').count()
    
    # Plots by type
    plots_by_type = []
    for type_code, type_name in tbl_plot_for_sale.PLOT_TYPE_CHOICES:
        count = tbl_plot_for_sale.objects.filter(plot_type=type_code).count()
        if count > 0:
            plots_by_type.append({
                'name': type_name,
                'count': count
            })
    
    # ========== USER STATISTICS ==========
    total_users = tbl_user.objects.count()
    
    # Users joined in period
    new_users = tbl_user.objects.filter(
        created_at__range=[start_date, end_date]
    ).count()
    
    # Users with properties
    users_with_properties = tbl_user.objects.annotate(
        prop_count=Count('properties')
    ).filter(prop_count__gt=0).count()
    
    # Users with plots
    users_with_plots = tbl_user.objects.annotate(
        plot_count=Count('plots')
    ).filter(plot_count__gt=0).count()
    
    # Top owners by property count
    top_property_owners = tbl_user.objects.annotate(
        property_count=Count('properties')
    ).filter(property_count__gt=0).order_by('-property_count')[:5]
    
    # Top owners by plot count
    top_plot_owners = tbl_user.objects.annotate(
        plot_count=Count('plots')
    ).filter(plot_count__gt=0).order_by('-plot_count')[:5]
    
    # ========== INTEREST STATISTICS ==========
    total_interests = tbl_plot_interest.objects.count()
    
    # Interests by status (if you have status field)
    # pending_interests = tbl_plot_interest.objects.filter(status='pending').count()
    # contacted_interests = tbl_plot_interest.objects.filter(status='contacted').count()
    
    # ========== CHART DATA ==========
    
    # Property creation trend (last 30 days)
    property_trend_labels = []
    property_trend_data = []
    
    for i in range(days-1, -1, -1):
        date = (timezone.now() - timedelta(days=i)).date()
        property_trend_labels.append(date.strftime('%d %b'))
        
        day_start = timezone.make_aware(datetime.combine(date, datetime.min.time()))
        day_end = timezone.make_aware(datetime.combine(date, datetime.max.time()))
        
        count = tbl_property.objects.filter(
            created_at__range=[day_start, day_end]
        ).count()
        property_trend_data.append(count)
    
    # Plot creation trend (last 30 days)
    plot_trend_data = []
    for i in range(days-1, -1, -1):
        date = (timezone.now() - timedelta(days=i)).date()
        day_start = timezone.make_aware(datetime.combine(date, datetime.min.time()))
        day_end = timezone.make_aware(datetime.combine(date, datetime.max.time()))
        
        count = tbl_plot_for_sale.objects.filter(
            created_at__range=[day_start, day_end]
        ).count()
        plot_trend_data.append(count)
    
    # Monthly data for the last 6 months
    monthly_labels = []
    monthly_properties = []
    monthly_plots = []
    monthly_users = []
    
    for i in range(5, -1, -1):
        month_date = timezone.now() - timedelta(days=30*i)
        month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        if i > 0:
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(microseconds=1)
        else:
            month_end = timezone.now()
        
        monthly_labels.append(month_start.strftime('%b %Y'))
        
        monthly_properties.append(tbl_property.objects.filter(
            created_at__range=[month_start, month_end]
        ).count())
        
        monthly_plots.append(tbl_plot_for_sale.objects.filter(
            created_at__range=[month_start, month_end]
        ).count())
        
        monthly_users.append(tbl_user.objects.filter(
            created_at__range=[month_start, month_end]
        ).count())
    
    # Price ranges
    property_price_ranges = {
        'under_10k': tbl_property.objects.filter(rent_amount__lt=10000).count(),
        '10k_20k': tbl_property.objects.filter(rent_amount__gte=10000, rent_amount__lt=20000).count(),
        '20k_30k': tbl_property.objects.filter(rent_amount__gte=20000, rent_amount__lt=30000).count(),
        '30k_50k': tbl_property.objects.filter(rent_amount__gte=30000, rent_amount__lt=50000).count(),
        'above_50k': tbl_property.objects.filter(rent_amount__gte=50000).count(),
    }
    
    plot_price_ranges = {
        'under_5l': tbl_plot_for_sale.objects.filter(price__lt=500000).count(),
        '5l_10l': tbl_plot_for_sale.objects.filter(price__gte=500000, price__lt=1000000).count(),
        '10l_20l': tbl_plot_for_sale.objects.filter(price__gte=1000000, price__lt=2000000).count(),
        '20l_50l': tbl_plot_for_sale.objects.filter(price__gte=2000000, price__lt=5000000).count(),
        'above_50l': tbl_plot_for_sale.objects.filter(price__gte=5000000).count(),
    }
    
    # Location wise distribution (top 5)
    top_locations_property = tbl_property.objects.values('location').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    top_locations_plot = tbl_plot_for_sale.objects.values('address').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    context = {
        # Date range
        'days': days,
        'start_date': start_date.date(),
        'end_date': end_date.date(),
        
        # Property stats
        'total_properties': total_properties,
        'pending_properties': pending_properties,
        'approved_properties': approved_properties,
        'rejected_properties': rejected_properties,
        'available_properties': available_properties,
        'occupied_properties': occupied_properties,
        'maintenance_properties': maintenance_properties,
        'furnished_properties': furnished_properties,
        'semi_furnished': semi_furnished,
        'unfurnished_properties': unfurnished_properties,
        'properties_1bhk': properties_1bhk,
        'properties_2bhk': properties_2bhk,
        'properties_3bhk': properties_3bhk,
        'properties_4plus': properties_4plus,
        'properties_by_category': properties_by_category,
        'recent_properties': recent_properties,
        
        # Plot stats
        'total_plots': total_plots,
        'pending_plots': pending_plots,
        'approved_plots': approved_plots,
        'rejected_plots': rejected_plots,
        'available_plots': available_plots,
        'sold_plots': sold_plots,
        'reserved_plots': reserved_plots,
        'plots_by_type': plots_by_type,
        
        # User stats
        'total_users': total_users,
        'new_users': new_users,
        'users_with_properties': users_with_properties,
        'users_with_plots': users_with_plots,
        'top_property_owners': top_property_owners,
        'top_plot_owners': top_plot_owners,
        
        # Interest stats
        'total_interests': total_interests,
        
        # Chart data
        'property_trend_labels': property_trend_labels,
        'property_trend_data': property_trend_data,
        'plot_trend_data': plot_trend_data,
        'monthly_labels': monthly_labels,
        'monthly_properties': monthly_properties,
        'monthly_plots': monthly_plots,
        'monthly_users': monthly_users,
        'property_price_ranges': property_price_ranges,
        'plot_price_ranges': plot_price_ranges,
        'top_locations_property': top_locations_property,
        'top_locations_plot': top_locations_plot,
    }
    
    return render(request, 'admin_analytics.html', context)

def admin_restore_property(request, property_id):
    """Restore a rejected property listing"""
    if request.method == 'POST':
        prop = get_object_or_404(tbl_property, id=property_id)
        
        # Reset status to default
        prop.availability_status = 'Available'
        # Clear rejection data if you have these fields
        if hasattr(prop, 'rejection_reason'):
            prop.rejection_reason = ''
        if hasattr(prop, 'admin_status'):
            prop.admin_status = 'pending' # Or 'approved' depending on your logic
            
        prop.save()
        
        messages.success(request, f'Property "{prop.title}" has been restored successfully.')
    
    return redirect('admin_properties')

# Add this import if not already present
from django.db.models import Count
from UserApp.models import tbl_feedback  # Assuming tbl_feedback is in UserApp based on your previous imports

def admin_feedback_list(request):
    """View all feedback submitted by users with filtering and stats"""
    
    # Get filter parameters
    type_filter = request.GET.get('type', 'all')
    search_query = request.GET.get('search', '')
    
    # Base queryset
    feedbacks = tbl_feedback.objects.all().select_related(
        'user', 'user__login'
    ).order_by('-created_at')
    
    # Apply Type Filter
    if type_filter != 'all':
        feedbacks = feedbacks.filter(feedback_type=type_filter)
    
    # Apply Search Filter (Searches in Subject, Message, or User Name)
    if search_query:
        feedbacks = feedbacks.filter(
            Q(subject__icontains=search_query) |
            Q(message__icontains=search_query) |
            Q(user__name__icontains=search_query) |
            Q(user__login__email__icontains=search_query)
        )
    
    # Get Counts for Dashboard Cards
    total_feedback = tbl_feedback.objects.count()
    suggestions_count = tbl_feedback.objects.filter(feedback_type='suggestion').count()
    complaints_count = tbl_feedback.objects.filter(feedback_type='complaint').count()
    bugs_count = tbl_feedback.objects.filter(feedback_type='bug').count()
    technical_count = tbl_feedback.objects.filter(feedback_type='technical').count()
    
    context = {
        'feedbacks': feedbacks,
        'total_feedback': total_feedback,
        'suggestions_count': suggestions_count,
        'complaints_count': complaints_count,
        'bugs_count': bugs_count,
        'technical_count': technical_count,
        'current_type': type_filter,
        'search_query': search_query,
    }
    
    return render(request, 'admin_feedback_list.html', context)