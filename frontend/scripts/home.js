// scripts/home.js

window.addEventListener('DOMContentLoaded', () => {
    // Backend service URL in Docker Compose
    const backendUrl = 'http://backend:8000';

    const token = sessionStorage.getItem('token');
    const homeBtn = document.getElementById('home-btn');
    const getStartedBtn = document.getElementById('get-started-btn');
    const navButtons = document.getElementById('nav-buttons');

    if (token) {
        // Verify the token by calling the backend (optional but recommended)
        fetch(`${backendUrl}/auth/me`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
            }
        }).then(response => {
            if (response.ok) {
                // If the user is authenticated, redirect to the dashboard
                window.location.href = 'dashboard.html';

                // Update the Home button to redirect to the dashboard
                homeBtn.href = 'dashboard.html';

                // Update the Get Started button to redirect to the dashboard
                if (getStartedBtn) {
                    getStartedBtn.textContent = 'Go to Dashboard';
                    getStartedBtn.href = 'dashboard.html';
                }

                // Add a Logout button
                const logoutBtn = document.createElement('button');
                logoutBtn.textContent = 'Logout';
                logoutBtn.classList.add('btn');
                logoutBtn.addEventListener('click', () => {
                    sessionStorage.removeItem('token');
                    window.location.href = 'index.html';
                });
                navButtons.appendChild(logoutBtn);
            } else {
                // If token verification fails, remove token and redirect to login
                sessionStorage.removeItem('token');
                window.location.href = 'login.html';
            }
        }).catch(error => {
            console.error('Error verifying token:', error);
            sessionStorage.removeItem('token');
            window.location.href = 'login.html';
        });

    } else {
        // If the user is not authenticated, Home button takes them to the index
        homeBtn.href = 'index.html';

        // Ensure the Get Started button links to the login page
        if (getStartedBtn) {
            getStartedBtn.href = 'login.html';
        }
    }
});
