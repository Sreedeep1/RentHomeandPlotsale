from django.shortcuts import render,redirect, get_object_or_404
from .forms import *
from .models import *
from UserApp.models import tbl_plot_for_sale,tbl_property
def index(request):
    context={
        'plots': tbl_plot_for_sale.objects.all().prefetch_related('images'),
        'properties': tbl_property.objects.all().prefetch_related('images'),
    }
    print(context)
    return render(request,'index.html', context)
def login_view(request):
    return render(request,'login.html')



def user_registration(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)

        if form.is_valid():
            # Save login table
            login = tbl_login.objects.create(
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                userrole='User'   # change if needed
            )

            # Save user table
            tbl_user.objects.create(
                login=login,
                name=form.cleaned_data['name'],
                phone=form.cleaned_data['phone']
            )

            return redirect("login")  # change to your login url

    else:
        form = RegistrationForm()

    return render(request, "user_registration.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            loginobj = tbl_login.objects.get(email=email, password=password)

            # Session setup
            request.session['login_id'] = loginobj.id
            request.session['email'] = loginobj.email
            request.session['userrole'] = loginobj.userrole

            # Role based redirect
            if loginobj.userrole == "admin":
                return redirect("admin_dashboard")


            elif loginobj.userrole == "User":
                obj=tbl_user.objects.get(login=loginobj.id)
                request.session['user_id'] = obj.id

                return redirect("user_dashboard")

            else:
                return render(request, "login.html", {
                    "error": "Invalid role"
                })

        except tbl_login.DoesNotExist:
            return render(request, "login.html", {
                "error": "Invalid email or password"
            })

    return render(request, "login.html")


def admin_dashboard(request):
    """Admin dashboard with statistics and charts"""
    
    from django.utils import timezone
    from datetime import timedelta
    
    # Get date ranges
    today = timezone.now().date()
    last_week = today - timedelta(days=7)
    last_month = today - timedelta(days=30)
    
    # Property statistics
    total_properties = tbl_property.objects.count()
    # Using availability_status as per your model definition
    pending_properties = tbl_property.objects.filter(availability_status='Available').count()
    approved_properties = tbl_property.objects.filter(availability_status='Occupied').count()
    rejected_properties = tbl_property.objects.filter(availability_status='Maintenance').count()
    
    # Plot statistics
    total_plots = tbl_plot_for_sale.objects.count()
    available_plots = tbl_plot_for_sale.objects.filter(availability_status='Available').count()
    sold_plots = tbl_plot_for_sale.objects.filter(availability_status='Sold').count()
    reserved_plots = tbl_plot_for_sale.objects.filter(availability_status='Reserved').count()
    
    # User statistics
    total_users = tbl_user.objects.count()
    new_users_this_month = tbl_user.objects.filter(
        created_at__range=[last_month, today]
    ).count()
    
    # Recent activities
    recent_properties = tbl_property.objects.all().select_related('owner').order_by('-created_at')[:5]
    recent_plots = tbl_plot_for_sale.objects.all().select_related('owner').order_by('-created_at')[:5]
    
    # Chart data for last 7 days
    property_chart_labels = []
    property_chart_data = []
    
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        property_chart_labels.append(date.strftime('%a')) # e.g., Mon, Tue
        count = tbl_property.objects.filter(created_at__date=date).count()
        property_chart_data.append(count)

    plot_chart_labels = []
    plot_chart_data = []
    
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        plot_chart_labels.append(date.strftime('%a'))
        count = tbl_plot_for_sale.objects.filter(created_at__date=date).count()
        plot_chart_data.append(count)
    
    context = {
        'total_properties': total_properties,
        'pending_properties': pending_properties,
        'approved_properties': approved_properties,
        'rejected_properties': rejected_properties,
        
        'total_plots': total_plots,
        'available_plots': available_plots,
        'sold_plots': sold_plots,
        'reserved_plots': reserved_plots,
        
        'total_users': total_users,
        'new_users_this_month': new_users_this_month,
        
        'recent_properties': recent_properties,
        'recent_plots': recent_plots,
        
        'property_chart_labels': property_chart_labels,
        'property_chart_data': property_chart_data,
        'plot_chart_data': plot_chart_data,
    }
    
    return render(request, 'admin_home.html', context)

def user_dashboard(request):
    context={
        'plots': tbl_plot_for_sale.objects.all().prefetch_related('images'),
        'properties': tbl_property.objects.all().prefetch_related('images'),
    }
    return render(request,'user_home.html', context)

    
def logout_view(request):
    request.session.flush()   # clears all session data         # logs out the user
    return redirect('login')