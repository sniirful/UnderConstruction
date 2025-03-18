let email = document.querySelector('input[type=email]');
let password = document.querySelector('input[type=password]');
document.querySelector('form').addEventListener('submit', async e => {
    e.preventDefault();

    let response = await fetch('/api/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            email: email.value,
            password: password.value
        })
    });
    if (response.status !== 200) return alert('Wrong credentials.');

    window.location.href = '/home';
});
