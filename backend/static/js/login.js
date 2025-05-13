document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('login-form');
    const errorDiv = document.getElementById('login-error');

    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const username = document.getElementById('login-username').value.trim();
            const password = document.getElementById('login-password').value;
            
            // Clear previous errors
            errorDiv.textContent = '';
            
            // Client-side validation
            if (!username || username.length < 3) {
                errorDiv.textContent = 'Username must be at least 3 characters.';
                return;
            }
            
            if (!password || password.length < 8) {
                errorDiv.textContent = 'Password must be at least 8 characters.';
                return;
            }
            
            // Send login request
            fetch('/php_auth/login.php', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    window.location.href = '/';
                } else {
                    errorDiv.textContent = (data.errors || ['Login failed']).join(' ');
                }
            })
            .catch(() => {
                errorDiv.textContent = 'Login failed. Please try again.';
            });
        });
    }
}); 