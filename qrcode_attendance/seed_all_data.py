import os
import django
import sys
import random
from datetime import datetime, timedelta, time
from django.utils import timezone

# Tenter d'importer Faker, sinon informer l'utilisateur
try:
    from faker import Faker
except ImportError:
    print("Erreur: Le package 'faker' n'est pas installé.")
    print("Veuillez exécuter: pip install faker")
    sys.exit(1)

# Setup Django
# sys.path.append('e:/Projet/Tous les projet mande/Flutter/qrcode_attendance')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()


from apps.employees.models import Employee, Department
from apps.attendance.models import Attendance

def seed_data():
    # Vérification si les données existent déjà
    if Employee.objects.count() > 1: # > 1 car l'admin peut déjà exister
        print("--- Les données existent déjà. Fin du script de seeding. ---")
        return

    fake = Faker('fr_FR')
    print("--- Démarrage du seed massif des données avec Faker ---")


    # 1. Création des 8 départements
    depts_names = [
        "Direction Générale", 
        "Informatique & Cloud", 
        "Ressources Humaines", 
        "Logistique & Supply", 
        "Commercial & Ventes",
        "Marketing & Communication", 
        "Finance & Comptabilité",
        "Support Technique"
    ]
    
    depts = []
    for name in depts_names:
        d, _ = Department.objects.get_or_create(name=name)
        depts.append(d)
    print(f"OK: {len(depts)} départements créés.")

    # 2. Création des employés (15 par département = 120 employés)
    employees = []
    
    # Création d'un admin par défaut si inexistant
    admin, created = Employee.objects.get_or_create(
        email="admin@pointagepro.mg",
        defaults={
            "first_name": "Super",
            "last_name": "Admin",
            "role": Employee.Role.ADMIN,
            "is_active": True,
            "is_staff": True,
            "is_superuser": True,
            "department": depts[0]
        }
    )
    if created:
        admin.set_password("admin123")
        admin.save()
        print("OK: Compte admin créé (admin@pointagepro.mg / admin123)")

    print("Génération de 120 employés uniques...")
    for dept in depts:
        for _ in range(15):
            f_name = fake.first_name()
            l_name = fake.last_name()
            # On génère un email unique basé sur le nom
            email_base = f"{f_name.lower()}.{l_name.lower()}"
            email = f"{email_base}@attendance.mg"
            
            # Gestion des doublons d'email (très probable avec 120 users)
            counter = 1
            while Employee.objects.filter(email=email).exists():
                email = f"{email_base}{counter}@attendance.mg"
                counter += 1

            emp = Employee.objects.create_user(
                email=email,
                first_name=f_name,
                last_name=l_name,
                department=dept,
                role=Employee.Role.EMPLOYEE,
                password="password123"
            )
            employees.append(emp)
    
    print(f"OK: {len(employees)} employés créés avec succès.")

    # 3. Génération des pointages (du 6 avril au 20 avril)
    start_date = datetime(2026, 4, 6).date()
    end_date = datetime(2026, 4, 20).date()
    
    current_date = start_date
    attendance_count = 0
    
    print(f"En cours: Génération des pointages du {start_date} au {end_date}...")

    while current_date <= end_date:
        is_weekend = current_date.weekday() >= 5
        
        for emp in employees:
            # Chance de présence : Week-end (5%) / Semaine (92%)
            presence_chance = 0.05 if is_weekend else 0.92
            
            if random.random() > presence_chance:
                continue

            # Heure d'arrivée (Check-IN) : entre 07:30 et 08:30
            arrival_hour = 7 if random.random() > 0.5 else 8
            if arrival_hour == 7:
                arrival_minute = random.randint(30, 59)
            else:
                arrival_minute = random.randint(0, 30)
            
            check_in_dt = timezone.make_aware(
                datetime.combine(current_date, time(arrival_hour, arrival_minute))
            )

            # Heure de départ (Check-OUT) : entre 16:30 et 18:30
            departure_hour = random.randint(16, 18)
            departure_minute = random.randint(0, 59) if departure_hour < 18 else random.randint(0, 30)
            
            check_out_dt = timezone.make_aware(
                datetime.combine(current_date, time(departure_hour, departure_minute))
            )

            Attendance.objects.create(
                employee=emp,
                check_in_time=check_in_dt,
                check_out_time=check_out_dt,
                status=Attendance.Status.COMPLETED
            )
            attendance_count += 1
            
        current_date += timedelta(days=1)

    print(f"OK: {attendance_count} enregistrements de présence générés.")
    print("--- Terminé avec succès ! ---")

if __name__ == "__main__":
    seed_data()
