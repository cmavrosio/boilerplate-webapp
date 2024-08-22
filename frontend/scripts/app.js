// scripts/app.js
// Load user data on the dashboard
window.addEventListener('DOMContentLoaded', async (event) => {
    const token = getToken();
    if (token) {
        try {
            const response = await fetch('http://localhost:8000/me/', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                const user = await response.json();
                document.getElementById('welcome-message').textContent = `Welcome, ${user.full_name}!`;
            } else {
                console.error('Failed to fetch user:', await response.text());
            }
        } catch (error) {
            console.error('Error during fetch:', error);
        }
    } else {
        // If no token is found, redirect to the login page
        window.location.href = 'login.html';
    }
});

// scripts/app.js

document.addEventListener('DOMContentLoaded', async function() {
    const backendUrl = 'http://localhost:8000';
    const token = sessionStorage.getItem('token');

    if (token) {
        try {
            const response = await fetch(`${backendUrl}/me/`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                const user = await response.json();
                document.getElementById('welcome-message').textContent = `Welcome, ${user.full_name}!`;
            } else {
                console.error('Failed to fetch user:', await response.text());
            }
        } catch (error) {
            console.error('Error during fetch:', error);
        }
    } else {
        // Redirect to the login page if there's no token
        window.location.href = 'login.html';
    }
});