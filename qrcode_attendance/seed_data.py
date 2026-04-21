import os
import django
import sys
import random
from datetime import datetime, timedelta, time
from django.utils import timezone

# Setup Django
sys.path.append('e:/Projet/Tous les projet mande/Flutter/qrcode_attendance')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.employees.models import Employee, Department
from apps.attendance.models import Attendance

def seed_data():
    print("--- Démarrage du seed des données ---")

    # 1. Création des départements
    depts_names = ["Direction", "Informatique", "Ressources Humaines", "Logistique", "Commercial"]
    depts = []
    for name in depts_names:
        d, _ = Department.objects.get_or_create(name=name)
        depts.append(d)
    print(f"OK: {len(depts)} départements créés/récupérés.")

    # 2. Création des employés
    employees_data = [
        {"email": "admin@attendance.mg", "first_name": "Admin", "last_name": "General", "role": "admin", "dept": depts[0]},
        {"email": "harena@attendance.mg", "first_name": "Harena", "last_name": "Dev", "role": "admin", "dept": depts[1]},
        {"email": "jean@attendance.mg", "first_name": "Jean", "last_name": "Dupont", "role": "employee", "dept": depts[1]},
        {"email": "marie@attendance.mg", "first_name": "Marie", "last_name": "Durand", "role": "employee", "dept": depts[2]},
        {"email": "toky@attendance.mg", "first_name": "Toky", "last_name": "Andria", "role": "employee", "dept": depts[3]},
        {"email": "sarah@attendance.mg", "first_name": "Sarah", "last_name": "Rasoa", "role": "employee", "dept": depts[4]},
    ]
    
    all_employees = []
    for data in employees_data:
        emp, created = Employee.objects.get_or_create(
            email=data["email"],
            defaults={
                "first_name": data["first_name"],
                "last_name": data["last_name"],
                "department": data["dept"],
                "role": data["role"],
                "is_active": True,
                "is_staff": data["role"] == "admin"
            }
        )
        if created:
            emp.set_password("password123")
            emp.save()
        all_employees.append(emp)
    print(f"OK: {len(all_employees)} employés créés/récupérés.")

    # 3. Création des pointages (30 derniers jours)
    print("En cours: Génération des pointages (30 jours)...")
    today = timezone.localdate()
    count = 0

    for i in range(30, 0, -1):
        current_date = today - timedelta(days=i)
        
        # Pas de pointage le weekend
        if current_date.weekday() >= 5:
            continue

        for emp in all_employees:
            # 80% de chance d'être présent
            if random.random() > 0.8:
                continue
            
            # Heure d'arrivée : entre 07h45 et 08h30
            arrival_minute = random.randint(-15, 30)
            check_in_dt = timezone.make_aware(
                datetime.combine(current_date, time(8, 0)) + timedelta(minutes=arrival_minute)
            )

            # Heure de départ : entre 16h30 et 18h00
            departure_hour = random.randint(16, 17)
            departure_minute = random.randint(0, 59)
            check_out_dt = timezone.make_aware(
                datetime.combine(current_date, time(departure_hour, departure_minute))
            )

            # Utiliser update_or_create pour éviter les doublons au cas où le script est relancé
            Attendance.objects.update_or_create(
                employee=emp,
                date=current_date,
                defaults={
                    "check_in_time": check_in_dt,
                    "check_out_time": check_out_dt,
                    "status": Attendance.Status.COMPLETED
                }
            )
            count += 1

    print(f"OK: {count} enregistrements de présence créés.")
    print("Terminé avec succès !")

if __name__ == "__main__":
    seed_data()
