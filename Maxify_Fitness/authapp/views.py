import email
import token

from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from authapp.models import Contact,MembershipPlan, Service,Trainer,Enrollment,Attendance,Gallery

# generated
import requests
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from authapp.models import PaystackConfiguration, UserMembership, WorkoutPlan
from django.utils import timezone
from datetime import timedelta
from authapp.models import PaystackConfiguration
from django.conf import settings

# Make users active when they signup
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator

# Token generation activation link
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model

# Create your views here.
def HomeView(request):
    return render(request, 'index.html')

def signup(request):
    if request.method=="POST":
        username=request.POST.get('usernumber')
        email=request.POST.get('email')
        pass1=request.POST.get('pass1')
        pass2=request.POST.get('pass2')
      
        if len(username)>10 or len(username)<10:
            messages.info(request,"Phone Number Must be 10 Digits")
            return redirect('/signup')

        if pass1!=pass2:
            messages.info(request,"Password is not Matching")
            return redirect('/signup')
       
        try:
            if User.objects.get(username=username):
                messages.warning(request,"Phone Number Already Taken")
                return redirect('/signup')
           
        except Exception as identifier:
            pass
        
        
        try:
            if User.objects.get(email=email):
                messages.warning(request,"Email already Exists")
                return redirect('/signup')
           
        except Exception as identifier:
            pass
             
        myuser = User.objects.create_user(username, email, pass1)
        myuser.is_active = False   # 👈 IMPORTANT
        myuser.save()

        # Generate activation link
        current_site = get_current_site(request)
        uid = urlsafe_base64_encode(force_bytes(myuser.pk))
        token = default_token_generator.make_token(myuser)

        activation_link = f"http://{current_site.domain}/activate/{uid}/{token}/"

        # Email content
        mail_subject = "Activate Your Account"
        message = f"""
        Hi {myuser.username},

        Click the link below to activate your account:

        {activation_link}

        If you did not register, ignore this email.
        """

        email = EmailMessage(
            mail_subject,
            message,
            to=[myuser.email],
        )
        email.send()

        messages.success(request, "Account created! Please check your email to activate your account.")
        return redirect('/login')
        
        
    return render(request,"signup.html")

# Activation email
User = get_user_model()

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Account activated successfully! You can now login.")
        return redirect('/login')
    else:
        messages.error(request, "Activation link is invalid!")
        return redirect('/')



# def handlelogin(request):
#     if request.method=="POST":        
#         username=request.POST.get('usernumber')
#         pass1=request.POST.get('pass1')
#         myuser=authenticate(username=username,password=pass1)
#         if myuser is not None:
#             login(request,myuser)
#             messages.success(request,"Login Successful")
#             return redirect('/')
#         else:
#             messages.error(request,"Invalid Credentials")
#             return redirect('/login')
            
        
#     return render(request,"handlelogin.html")

def handlelogin(request):
    if request.method == "POST":
        username = request.POST.get('usernumber')
        pass1 = request.POST.get('pass1')

        user = authenticate(username=username, password=pass1)

        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, "Login Successful")
                return redirect('/')
            else:
                messages.warning(request, "Your account is not activated. Please check your email.")
                return redirect('/login')

        else:
            # Check if user exists but is inactive
            try:
                existing_user = User.objects.get(username=username)
                if not existing_user.is_active:
                    messages.warning(request, "Your account is not activated. Please check your email.")
                else:
                    messages.error(request, "Invalid Credentials")
            except User.DoesNotExist:
                messages.error(request, "Invalid Credentials")

            return redirect('/login')

    return render(request, "handlelogin.html")

#resend activation link
def resend_activation(request):
    if request.method == "POST":
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)

            if user.is_active:
                messages.info(request, "Account already activated.")
                return redirect('/login')

            # Generate new activation link
            current_site = get_current_site(request)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            activation_link = f"http://{current_site.domain}/activate/{uid}/{token}/"

            mail_subject = "Activate Your Account"
            message = f"""
Hi {user.username},

Click the link below to activate your account:

{activation_link}
"""

            email_message = EmailMessage(
                mail_subject,
                message,
                to=[user.email],
            )
            email_message.send()

            messages.success(request, "Activation email resent. Check your inbox.")
            return redirect('/login')

        except User.DoesNotExist:
            messages.error(request, "No account found with this email.")
            return redirect('/resend-activation')

    return render(request, "resend_activation.html")





def handleLogout(request):
    logout(request)
    messages.success(request,"Logout Success")    
    return redirect('/login')

def contact(request):
    if request.method=="POST":
        name=request.POST.get('fullname')
        email=request.POST.get('email')
        number=request.POST.get('num')
        desc=request.POST.get('desc')
        myquery=Contact(name=name,email=email,phonenumber=number,description=desc)
        myquery.save()       
        messages.info(request,"Thank you for Contacting us we will get back you soon")
        return redirect('/contact')
        
    return render(request,"contact.html")

def Enroll(request):
    if not request.user.is_authenticated:
        messages.warning(request,"Please Login and Try Again")
        return redirect('/login')

    Membership=MembershipPlan.objects.all()
    SelectTrainer=Trainer.objects.all()
    context={"Membership":Membership,"SelectTrainer":SelectTrainer}
    if request.method=="POST":
        FullName=request.POST.get('FullName')
        email=request.POST.get('email')
        gender=request.POST.get('gender')
        PhoneNumber=request.POST.get('PhoneNumber')
        DOB=request.POST.get('DOB')
        member=request.POST.get('member')
        trainer=request.POST.get('trainer')
        reference=request.POST.get('reference')
        address=request.POST.get('address')
        query=Enrollment(FullName=FullName,Email=email,Gender=gender,PhoneNumber=PhoneNumber,DOB=DOB,SelectMembershipplan=member,SelectTrainer=trainer,Reference=reference,Address=address)
        query.save()
        messages.success(request,"Enrollment successful")
        return redirect('/enroll')



    return render(request,"enroll.html",context)

def Profile(request):
    if not request.user.is_authenticated:
        messages.warning(request,"Please Login and Try Again")
        return redirect('/login')
    user_phone=request.user
    posts=Enrollment.objects.filter(PhoneNumber=user_phone)
    attendance=Attendance.objects.filter(phonenumber=user_phone)
    print(posts)
    context={"posts":posts,"attendance":attendance}
    return render(request,"profile.html",context)


def gallery_view(request):
    posts=Gallery.objects.all()
    context={"posts":posts}
    return render(request,"gallery.html",context)

def attendance_view(request):
    if not request.user.is_authenticated:
        messages.warning(request,"Please Login and Try Again")
        return redirect('/login')
    SelectTrainer=Trainer.objects.all()
    context={"SelectTrainer":SelectTrainer}
    if request.method=="POST":
        phonenumber=request.POST.get('PhoneNumber')
        Login=request.POST.get('logintime')
        Logout=request.POST.get('loginout')
        SelectWorkout=request.POST.get('workout')
        TrainedBy=request.POST.get('trainer')
        query=Attendance(phonenumber=phonenumber,Login=Login,Logout=Logout,SelectWorkout=SelectWorkout,TrainedBy=TrainedBy)
        query.save()
        messages.warning(request,"Attendance Applied Successfully")
        return redirect('/attendance')
    return render(request,"attendance.html",context)

def About(request):
    return render(request,"about.html")

def Services(request):
    services = Service.objects.all()
    context = {
        "services": services
    }

    return render(request,"services.html",context)

def Checkout(request):
    return render(request,"checkout.html")

def Pricing(request):
    plans = MembershipPlan.objects.all()
    context = {
        "plans": plans
    }
    return render(request, "pricing.html", context)
# --generated--

def create_checkout_session(request):
    if request.method == 'POST':
        # You'll get this ID from your Stripe Dashboard product settings
        price_id = request.POST.get('price_id') 
        
        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',  # Use 'subscription' for recurring gym fees
                success_url=request.build_absolute_uri('/payment-success/'),
                cancel_url=request.build_absolute_uri('/payment-cancelled/'),
            )
            return redirect(checkout_session.url, code=303)
        except Exception as e:
            return f"Error: {str(e)}"
 # Initialize Payment

# def initialize_paystack_payment(request):
#     # Fetch keys from Admin Dashboard
#     config = get_object_or_404(PaystackConfiguration, is_active=True)
    
#     if request.method == "POST":
#         email = request.user.email
#         amount = request.POST.get('amount')
#         amount_kobo = int(amount) * 100 

#         url = "https://api.paystack.co/transaction/initialize"
#         headers = {
#             "Authorization": f"Bearer {config.secret_key}", # Dynamic Secret Key
#             "Content-Type": "application/json",
#         }
# #         response = requests.post(url, headers=headers, json=data)
#         res_data = response.json()

#         if res_data['status']:
#             # Redirect user to Paystack Payment Page
#             return redirect(res_data['data']['authorization_url'])
        
#     return redirect('pricing')

@login_required
def paystack_init(request):

    config = PaystackConfiguration.objects.filter(is_active=True).first()

    if not config:
        messages.error(request,"Payment system not configured")
        return redirect('pricing')


    amount = request.POST.get('amount')
    plan = request.POST.get('plan')
    days = request.POST.get('days')


    request.session['plan'] = plan
    request.session['days'] = days
    request.session['amount'] = amount


    url = "https://api.paystack.co/transaction/initialize"

    headers = {
        "Authorization": f"Bearer {config.secret_key}",
        "Content-Type": "application/json"
    }

    data = {
        "email": request.user.email,
        "amount": int(amount)*100,
        "callback_url": request.build_absolute_uri('/verify/')
    }


    res = requests.post(url, headers=headers, json=data).json()


    if res['status']:
        return redirect(res['data']['authorization_url'])


    messages.error(request,"Payment failed")
    return redirect('pricing')

# Freeze/Unfreeze Logic
@login_required
def toggle_freeze(request):

    m = request.user.memberships.filter(is_active=True).order_by('-start_date').first()

    today = timezone.now().date()

    expiry = m.expiry_date

    # Convert if datetime
    if hasattr(expiry, "date"):
        expiry = expiry.date()

    if not m.is_frozen:

        remaining_days = (expiry - today).days

        m.remaining_days_at_freeze = max(remaining_days, 0)
        m.is_frozen = True

    else:

        m.expiry_date = today + timedelta(days=m.remaining_days_at_freeze)
        m.is_frozen = False

    m.save()

    return redirect('dashboard')


# uploading workout plans (trainers only)
# Check if the user is in the 'Trainers' group
def trainer(user):
    return user.groups.filter(name='Trainers').exists() or user.is_superuser

@user_passes_test(trainer)
def trainer_upload(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        pdf = request.FILES.get('pdf_file')
        level = request.POST.get('level')
        
        WorkoutPlan.objects.create(
            title=title,
            pdf_file=pdf,
            membership_level=level
        )
        messages.success(request, "Workout plan uploaded successfully!")
        return redirect(trainer_upload)
    
    return render(request, 'trainer/upload.html')


# member dashboard
# @login_required
# def member_dashboard(request):
#     # Get the user's membership details
#     membership = getattr(request.user, 'usermembership', None)
    
#     # Optional: Get all past successful payments for this user
#     payment_history = UserMembership.objects.filter(user=request.user).order_by('-start_date')

#     context = {
#         'membership': membership,
#         'history': payment_history,
#     }
#     return render(request, 'dashboard.html', context)


# view protection Gatekeeper for active members only
def active_member_required(view_func):
    @login_required
    def _wrapped_view(request, *args, **kwargs):

        membership = request.user.memberships.filter(
            is_active=True
        ).order_by('-start_date').first()

        if not membership:
            messages.warning(request, "You need an active membership.")
            return redirect('pricing')

        if membership.has_expired:
            messages.warning(request, "Your membership has expired.")
            return redirect('pricing')

        return view_func(request, *args, **kwargs)

    return _wrapped_view

# Usage:
@login_required
def member_dashboard(request):

    # Get latest active membership
    membership = request.user.memberships.filter(
        is_active=True
    ).order_by('-start_date').first()

    # Get full payment history
    payment_history = request.user.memberships.all().order_by('-start_date')

    # Default values
    days_remaining = 0
    progress_percentage = 0
    workout_plans = []

    if membership:

        # If expired, mark inactive automatically
        if membership.has_expired:
            membership.is_active = False
            membership.save(update_fields=["is_active"])

        # Calculate days remaining safely
        if membership.expiry_date:
            now = timezone.now()

            if membership.expiry_date > now:
                days_remaining = (membership.expiry_date - now).days
            else:
                days_remaining = 0

            # Calculate total duration dynamically
            if membership.start_date:
                total_duration = (membership.expiry_date - membership.start_date).days

                if total_duration > 0:
                    progress_percentage = int(
                        (days_remaining / total_duration) * 100
                    )

        # Load workout plans only if membership valid
        if not membership.is_frozen and not membership.has_expired:
            workout_plans = WorkoutPlan.objects.all()

    context = {
        "membership": membership,
        "history": payment_history,
        "days_remaining": days_remaining,
        "progress_percentage": progress_percentage,
        "workout_plans": workout_plans,
    }

    return render(request, "dashboard.html", context)


# paystack payment verification
def verify_payment(request):
    reference = request.GET.get('reference')
    
    # 1. Get your secret key from the Admin Config model we built
    config = PaystackConfiguration.objects.get(is_active=True)
    # 2. Define res_data by actually calling the Paystack API
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {"Authorization": f"Bearer {config.secret_key}"}
    
    response = requests.get(url, headers=headers)
    res_data = response.json()  # <--- This line defines res_data and removes the yellow line!

    # 3. Now you can safely use res_data
    if res_data.get('status') and res_data['data']['status'] == 'success':
        user = request.user
        amount = res_data['data']['amount'] / 100 
        days = int(request.session.get('days',30))
        plan = request.session.get('plan',"Basic")
        amount = request.session.get('amount',0)

        expiry = timezone.now() + timedelta(days=days)

        # Deactivate old active memberships
        UserMembership.objects.filter(
            user=user,
            is_active=True
        ).update(is_active=False)

        # Create new active membership
        membership = UserMembership.objects.create(
            user=user,
            plan_name=plan,
            paystack_ref=reference,
            amount_paid=amount,
            expiry_date=expiry,
            is_active=True,
        )
        return render(request, 'success.html', {'membership': membership})
    
    return render(request, 'failure.html')

#workout plan pdf download
@login_required
def workout_library(request):

    membership = getattr(request.user, 'usermembership', None)

    if not membership:
        messages.warning(request,"You need a membership")
        return redirect('pricing')

    # Elite sees everything
    if "ELITE" in membership.plan_name.upper():
        workouts = WorkoutPlan.objects.all()

    else:
        workouts = WorkoutPlan.objects.filter(
            membership_level="BASIC"
        )

    context = {
        "workouts": workouts
    }

    return render(request,"workouts.html",context)


# Payment History
@login_required
def payment_history(request):

    memberships = UserMembership.objects.filter(
        user=request.user
    ).order_by('-start_date')

    context = {
        "memberships": memberships
    }

    return render(request, "payment_history.html", context)