document.addEventListener('DOMContentLoaded', function() {
    const backendUrl = 'http://localhost:8000';  // Adjust as necessary for Docker

    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            const formData = new FormData();
            formData.append('username', document.getElementById('login-email').value);
            formData.append('password', document.getElementById('login-password').value);

            try {
                const response = await fetch(`${backendUrl}/token`, {
                    method: 'POST',
                    body: formData,
                });

                if (response.ok) {
                    const data = await response.json();
                    console.log("Received token:", data.access_token);
                
                    // Store the token in sessionStorage
                    sessionStorage.setItem('token', data.access_token);
                
                    // Redirect to the dashboard
                    console.log('Redirecting to dashboard...');
                    window.location.href = 'dashboard.html';
                } else {
                    const errorData = await response.json();
                    console.error('Login failed:', errorData);
                    alert('Login failed: ' + errorData.detail);
                }
            } catch (error) {
                console.error('Error during login:', error);
                alert('An error occurred during login. Please try again.');
            }
        });
    }

    const logoutButton = document.getElementById('logout-btn');
    if (logoutButton) {
        logoutButton.addEventListener('click', function() {
            sessionStorage.removeItem('token');
            window.location.href = 'login.html';
        });
    }

    const signupForm = document.getElementById('signup-form');
    if (signupForm) {
        signupForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const password = document.getElementById('signup-password').value;
            const passwordVerify = document.getElementById('signup-password-verify').value;
    
            if (password !== passwordVerify) {
                alert('Passwords do not match. Please try again.');
                return;
            }
    
            const signupData = {
                full_name: document.getElementById('signup-full_name').value,
                email: document.getElementById('signup-email').value,
                password: password
            };
    
            try {
                const response = await fetch(`${backendUrl}/users/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(signupData),
                });
    
                if (response.ok) {
                    const data = await response.json();
                    console.log("Signup successful:", data);
                
                    // Check if a token is returned and store it in sessionStorage
                    if (data.access_token) {
                        console.log("Received token:", data.access_token);
                        sessionStorage.setItem('token', data.access_token);
                    }
                
                    // Redirect to the login page
                    window.location.href = 'login.html';
                } else {
                    const errorData = await response.json();
                    console.error('Signup failed:', errorData);
                    alert('Signup failed: ' + errorData.detail);
                }
            } catch (error) {
                console.error('Error during signup:', error);
                alert('An error occurred during signup. Please try again.');
            }
        });
    }
});