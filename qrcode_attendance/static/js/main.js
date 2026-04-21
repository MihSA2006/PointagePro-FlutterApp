/**
 * Logic for the Admin Dashboard Template 
 */

document.addEventListener('DOMContentLoaded', () => {

    // Sidebar Navigation Logic
    const menuItems = document.querySelectorAll('.menu-item');
    const sections = document.querySelectorAll('.dashboard-section');

    menuItems.forEach(item => {
        item.addEventListener('click', function () {
            // Remove active class from all menu items
            menuItems.forEach(mi => mi.classList.remove('active'));
            // Add active class to clicked item
            this.classList.add('active');

            // Hide all sections
            sections.forEach(section => section.classList.remove('active'));

            // Show target section
            const targetId = this.getAttribute('data-target');
            if (targetId) {
                const targetSection = document.getElementById(targetId);
                if (targetSection) {
                    targetSection.classList.add('active');
                }
            }

            // Close mobile sidebar if open
            const sidebar = document.getElementById('sidebar');
            if (window.innerWidth <= 992 && sidebar.classList.contains('open')) {
                sidebar.classList.remove('open');
            }
        });
    });

    // Mobile Menu Toggle
    const menuToggle = document.getElementById('menuToggle');
    const sidebar = document.getElementById('sidebar');

    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', () => {
            sidebar.classList.toggle('open');
        });
    }

    // Auto-update Date
    const dateElement = document.getElementById('currentDate');
    if (dateElement) {
        const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        const today = new Date();
        dateElement.textContent = today.toLocaleDateString('fr-FR', options);
    }

    // Close modals on clicking overlay background
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', function (e) {
            if (e.target === this) {
                this.classList.remove('active');
            }
        });
    });
});

// Modal Functions
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
    }
}

// Mock QR Generation function
function generateQR() {
    const placeholder = document.getElementById('qrPlaceholder');
    const result = document.getElementById('qrResult');

    if (placeholder && result) {
        placeholder.style.display = 'none';
        result.style.display = 'flex';

        // Simutate adding a small animation or toast
        const btn = event.currentTarget;
        const originalText = btn.innerHTML;
        btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Génération...';
        btn.disabled = true;

        setTimeout(() => {
            btn.innerHTML = '<i class="fa-solid fa-check"></i> Code Généré';
            btn.classList.replace('btn-primary', 'btn-secondary');

            setTimeout(() => {
                btn.innerHTML = originalText;
                btn.classList.replace('btn-secondary', 'btn-primary');
                btn.disabled = false;
            }, 2000);
        }, 800);
    }
}
