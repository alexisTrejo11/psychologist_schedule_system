"use strict";

document.addEventListener('DOMContentLoaded', function () {
    // DOM
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('mainContent');
    const menuToggle = document.getElementById('menuToggle');
    const navLinks = document.querySelectorAll('.sidebar a');
    const allpages = document.querySelectorAll('.page-content');

    // CRUD Buttons
    const newSessionBtn = document.getElementById('newSessionBtn');
    const cancelSessionBtn = document.getElementById('cancelSessionBtn');
    const newPaymentBtn = document.getElementById('newPaymentBtn');
    const cancelPaymentBtn = document.getElementById('cancelPaymentBtn');

    // Forms
    const profileForm = document.getElementById('profileForm');
    const passwordForm = document.getElementById('passwordForm');
    const sessionForm = document.getElementById('sessionForm');
    const paymentForm = document.getElementById('paymentForm');
    const patientForm = document.getElementById('patientForm');


    // User Settings
    const userToggle = document.getElementById("userMenuToggle");
    const dropdown = document.getElementById("userDropdown");

    // APP state
    let currentPage = 'dashboard';
    let isLoggedIn = true;
    let authToken = localStorage.getItem('access_token');

    /*
    if (authToken) {
        isLoggedIn = true;
    } 
    */

    
    // Nav State Functions
    function showPage(pageId) {
        currentPage = pageId;
        
        allpages.forEach(page => {
            page.classList.add('hidden');
        });

        const selectedPage = document.getElementById(pageId);
        console.log(pageId)
        console.log(selectedPage)
        if (selectedPage) {
            selectedPage.classList.remove('hidden');
        }

        navLinks.forEach(link => {
            const linkPage = link.hasAttribute('data-page');
            if (linkPage === pageId) {
                link.classList.add('active')
                console.log(link)
            } else {
                link.classList.remove('active')
            }
        });
    }

    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();

            const pageId = this.getAttribute('data-page');

            if (pageId === 'logout') {
                logout();
                return;
              }
            
            showPage(pageId);
        });
    });


    // User Config
    userToggle.addEventListener("click", () => {
        dropdown.classList.toggle("hidden");
    });

    document.addEventListener("click", (e) => {
        const userMenu = document.getElementById("userMenu");
        if (!userMenu.contains(e.target)) {
            dropdown.classList.add("hidden");
        }
    });

    function initApp() {
        if (!isLoggedIn) {
            showPage('login');
        } else {
            showPage('dashboard');
        }
    }

    initApp();
});
