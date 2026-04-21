from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from apps.employees.models import Employee, Department
from apps.attendance.models import Attendance, QRCodeSession
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, timedelta

def superuser_required(user):
    return user.is_authenticated and user.is_superuser

def admin_login(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('dashboard:index')
        
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            if user.is_superuser:
                login(request, user)
                return redirect('dashboard:index')
            else:
                messages.error(request, "Accès refusé. Seuls les super-administrateurs peuvent accéder à cette interface.")
        else:
            messages.error(request, "Identifiants invalides.")
            
    return render(request, "dashboard/login.html")

def admin_logout(request):
    logout(request)
    return redirect('dashboard:login')

@user_passes_test(superuser_required, login_url='dashboard:login')
def admin_dashboard(request):
    today = timezone.localdate()
    
    # --- Statistiques ---
    total_employees = Employee.objects.count()
    total_departments = Department.objects.count()
    present_today_count = Attendance.objects.filter(date=today).values('employee').distinct().count()
    absent_today_count = max(0, total_employees - present_today_count)
    
    # --- Filtres & Recherche : Effectif ---
    q_emp = request.GET.get('q_emp', '')
    dept_id = request.GET.get('dept_id', '')
    
    employees_list = Employee.objects.select_related('department').all()
    if q_emp:
        employees_list = employees_list.filter(
            Q(first_name__icontains=q_emp) | 
            Q(last_name__icontains=q_emp) | 
            Q(email__icontains=q_emp)
        )
    if dept_id and dept_id != 'all':
        employees_list = employees_list.filter(department_id=dept_id)
    
    # --- Filtres & Recherche : Historique Global ---
    q_hist = request.GET.get('q_hist', '')
    date_start = request.GET.get('date_start', '')
    date_end = request.GET.get('date_end', '')
    
    history_list = Attendance.objects.select_related('employee', 'employee__department').all().order_by('-created_at')
    if q_hist:
        history_list = history_list.filter(
            Q(employee__first_name__icontains=q_hist) | 
            Q(employee__last_name__icontains=q_hist) |
            Q(employee__email__icontains=q_hist)
        )
    if date_start:
        history_list = history_list.filter(date__gte=date_start)
    if date_end:
        history_list = history_list.filter(date__lte=date_end)

    # --- Pointages du Jour (Today Only) ---
    today_attendances = Attendance.objects.select_related('employee', 'employee__department').filter(date=today).order_by('-created_at')
    
    # --- Récents (pour la vue d'ensemble) ---
    recent_attendances = Attendance.objects.select_related('employee', 'employee__department').order_by('-created_at')[:10]
    
    departments = Department.objects.all()
    # Annotate departments for template selection (avoids template comparison issues)
    for dept in departments:
        dept.is_selected = (str(dept.id) == dept_id)
    
    # QR Codes du jour (filtrage par plage locale)
    local_now = timezone.localtime()
    today_start = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    today_qrcodes = QRCodeSession.objects.filter(
        created_at__gte=today_start, created_at__lt=today_end
    ).order_by('-created_at')
    
    context = {
        # Stats
        "total_employees": total_employees,
        "total_departments": total_departments,
        "present_today": present_today_count,
        "absent_today": absent_today_count,
        
        # Lists
        "recent_attendances": recent_attendances,
        "employees_list": employees_list,
        "history_list": history_list,
        "today_attendances": today_attendances,
        "today_qrcodes": today_qrcodes,
        "departments": departments,
        
        # Current Filters (to persist in UI)
        "q_emp": q_emp,
        "dept_id": dept_id,
        "q_hist": q_hist,
        "date_start": date_start,
        "date_end": date_end,
        
        "current_page": "dashboard"
    }
    return render(request, "dashboard/dashboard.html", context)

@user_passes_test(superuser_required, login_url='dashboard:login')
def add_employee(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        department_id = request.POST.get("department")
        
        try:
            dept = Department.objects.get(id=department_id) if department_id else None
            Employee.objects.create_user(
                email=email,
                first_name=first_name,
                last_name=last_name,
                department=dept,
                role=Employee.Role.EMPLOYEE,
                password="Employee123!" # Default password
            )
            messages.success(request, f"L'employé {first_name} {last_name} a été ajouté avec succès.")
        except Exception as e:
            messages.error(request, f"Erreur lors de l'ajout : {str(e)}")
            
    return redirect('dashboard:index')
