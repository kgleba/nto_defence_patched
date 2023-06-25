const loginButton = document.querySelector('#login-button');

function setCookie(name, value, days) {
    var expires = "";
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "") + expires + "; path=/";
}

if (loginButton) {
    loginButton.addEventListener('click', () => {
        const username = document.querySelector('#username').value;
        const password = document.querySelector('#password').value;

        const loginData = {username: username, password: password};

        fetch('/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(loginData)
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'ok') {
                    var user_id = data.user_id;
                    setCookie('user_id', user_id, 1);
                    window.location.href = '/home';
                } else {
                    alert('Invalid username or password');
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
    });
}

const registerButton = document.getElementById("register-button")
if (registerButton) {
    registerButton.addEventListener("click", function () {
        // Get the values from the input fields
        var username = document.getElementById("username").value;
        var email = document.getElementById("email").value;
        var password1 = document.getElementById("password1").value;
        var password2 = document.getElementById("password2").value;

        // Check if passwords match
        if (password1 != password2) {
            alert("Passwords do not match!");
            return;
        }

        // Create the data to be sent as JSON
        var data = {
            "username": username,
            "email": email,
            "password1": password1,
            "password2": password2
        };

        // Send the data as a POST request to the /register endpoint
        fetch("/register", {
            method: "POST",
            body: JSON.stringify(data),
            headers: {
                "Content-Type": "application/json"
            }
        }).then(function (response) {
            if (response.status == 400) {
                alert("Passwords do not match!");
            } else if (response.status == 403) {
                alert("User exists!");
            } else if (response.status == 200) {
                window.location.href = "/login";
            }
        });
    });
}
