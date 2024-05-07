// theme.js

document.addEventListener('DOMContentLoaded', (event) => {
    const loginButton = document.querySelector('button[type="submit"]');

    if (loginButton) {
        loginButton.addEventListener('mouseclick', function() {
            document.body.style.backgroundColor = '#ff00f7'; 
        });

        loginButton.addEventListener('mouseout', function() {
            document.body.style.backgroundColor = '';
        });
    }
});