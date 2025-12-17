import re
from .models import Student, Vote, Candidate, ElectionSettings
from django.db.models import Count
from django.http import HttpResponse
from django.core.mail import send_mail
from django.contrib.auth import logout
from django.shortcuts import render, redirect

def is_valid_student_id(student_id):
    """Checks if the student ID is a 5-digit number."""
    return re.match(r'^\d{5}$', student_id) is not None

# LOGIN PAGE
def login_page(request):
    error_message = None     
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        password = request.POST.get('password')
        try:
            user = Student.objects.get(student_id=student_id)
        except Student.DoesNotExist:
            error_message = 'Invalid ID or password'
            return render(request, 'login.html', {'error': error_message})

        if user.password != password:
            error_message = 'Invalid ID or password'
            return render(request, 'login.html', {'error': error_message})
        if user.role == 'admin':
            request.session['user_id'] = user.student_id
            request.session['role'] = user.role
            return redirect('admin_dashboard')

        if user.role == 'student':
            if not is_valid_student_id(student_id):
                error_message = 'Student ID must be a 5-digit number.'
                return render(request, 'login.html', {'error': error_message})

            request.session['user_id'] = user.student_id
            request.session['role'] = user.role

            if user.has_voted:
                return redirect('already_voted')

            return redirect('vote')
        error_message = 'Invalid user role.' 
        return render(request, 'login.html', {'error': error_message})
    return render(request, 'login.html', {'error': error_message})

# SIGNUP PAGE
def signup_page(request):
    error_message = None
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        password = request.POST.get('password')
        email_id = request.POST.get('email_id')

        is_admin_signup = (student_id.lower() == 'admin')
        is_student_id_valid = is_valid_student_id(student_id) 

        if not is_admin_signup and not is_student_id_valid:
            error_message = 'Registration ID must be the word "admin" or a 5-digit student number.'
            return render(request, 'signup.html', {'error': error_message})

        if Student.objects.filter(student_id=student_id).exists() or Student.objects.filter(email_id=email_id).exists():
            error_message = 'User ID or Email already registered!'
            return render(request, 'signup.html', {'error': error_message})

        user_role = 'student'
        if is_admin_signup:
            user_role = 'admin'
        
        Student.objects.create(
            student_id=student_id,
            password=password,
            email_id=email_id,
            role=user_role
        )

        send_mail(
            'Welcome to KIET Voting System!',
            f'Hi {student_id},\n\nYour account has been successfully created. You can now log in and cast your vote.\n\nThank you!',
            'shoaibnaqvi33@gmail.com',
            [email_id],
            fail_silently=False,
        )
        return redirect('login')
    return render(request, 'signup.html', {'error': error_message})

# VOTING PAGE (MAIN LOGIC)
def vote_page(request):
    if 'user_id' not in request.session:
        return redirect('login')

    student = Student.objects.get(student_id=request.session['user_id'])

    status_obj = ElectionSettings.objects.first()
    is_active = status_obj.is_active if status_obj else False

    if student.has_voted:
        return redirect('already_voted')
    
    if request.method == 'POST':
        if not is_active:
            return HttpResponse("Forbidden: Voting is currently closed by Admin.", status=403)

        president = request.POST.get('president')
        vice_president = request.POST.get('vice_president')
        secretary = request.POST.get('secretary')
        finance_manager = request.POST.get('finance_manager')

        Vote.objects.create(
            student=student,
            president=request.POST.get('president'),
            vice_president=request.POST.get('vice_president'),
            secretary=request.POST.get('secretary'),
            finance_manager=request.POST.get('finance_manager')
        )

        student.has_voted = True
        student.save()
        
        send_mail(
            'Vote Successfully Cast',
            f'Dear {student.student_id},\n\nYour vote has been securely recorded for the Student Society Club election.\n\nThank you for participating!',
            'shoaibnaqvi33@gmail.com',
            [student.email_id],
            fail_silently=False,
        )
        return redirect('success')
    candidates = Candidate.objects.all()

    return render(request, 'vote.html', {
        'candidates': Candidate.objects.all(),
        'election_status': is_active
    })

def success_page(request):
    return render(request, 'success.html')

def already_voted_page(request):
    return render(request, 'already_voted.html')

def admin_dashboard(request):
    if request.session.get('role') != 'admin':
        return redirect('login')
    
    total_votes = Vote.objects.count()
    total_voters = Student.objects.filter(role='student').count()
    votes_remaining = max(0, total_voters - total_votes)
    
    status_obj = ElectionSettings.objects.first()
    is_active = status_obj.is_active if status_obj else False

    return render(request, 'admin_dashboard.html', {
        'total_votes': total_votes,
        'total_voters': total_voters,
        'votes_remaining': votes_remaining,
        'election_status': is_active,
    })

def results_page(request):
    if request.session.get('role') != 'admin':
        return redirect('login') 

    president_results = Vote.objects.values('president').annotate(
        count=Count('president')
    ).order_by('-count')

    vice_president_results = Vote.objects.values('vice_president').annotate(
        count=Count('vice_president')
    ).order_by('-count')

    secretary_results = Vote.objects.values('secretary').annotate(
        count=Count('secretary')
    ).order_by('-count')

    finance_manager_results = Vote.objects.values('finance_manager').annotate(
        count=Count('finance_manager')
    ).order_by('-count')

    total_votes = Vote.objects.count()

    context = {
        'total_votes': total_votes,
        'president_results': president_results,
        'vice_president_results': vice_president_results,
        'secretary_results': secretary_results,
        'finance_manager_results': finance_manager_results,
    }

    return render(request, 'results.html', context)

def logout_view(request):
    logout(request)
    return redirect('login')

# View to manage candidates and status
def manage_election(request):
    if request.session.get('role') != 'admin':
        return redirect('login')

    candidates = Candidate.objects.all()
    status, created = ElectionSettings.objects.get_or_create(id=1)

    if request.method == 'POST':
        if 'add_candidate' in request.POST:
            name = request.POST.get('name')
            pos = request.POST.get('position')
            Candidate.objects.create(name=name, position=pos)
        
        elif 'remove_candidate' in request.POST:
            candidate_id = request.POST.get('candidate_id')
            Candidate.objects.filter(id=candidate_id).delete()
            
        elif 'toggle_status' in request.POST:
            status.is_active = not status.is_active
            status.save()

        return redirect('manage_election')

    return render(request, 'manage_election.html', {
        'candidates': candidates,
        'status': status
    })
