from django.core.management.base import BaseCommand
from apps.attendance.services import AttendanceService


class Command(BaseCommand):
    help = "Clôture automatiquement les pointages actifs (auto check-out)."

    def handle(self, *args, **options):
        self.stdout.write("Démarrage de l'auto check-out...")
        
        count = AttendanceService.auto_checkout_midnight()
        
        if count > 0:
            self.stdout.write(
                self.style.SUCCESS(f"Succès : {count} pointage(s) clôturé(s).")
            )
        else:
            self.stdout.write("Aucun pointage actif à clôturer.")
