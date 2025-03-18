let username = document.querySelector('input[type=text]');
let email = document.querySelector('input[type=email]');
let password = document.querySelector('input[type=password]');
document.querySelector('form').addEventListener('submit', async e => {
    e.preventDefault();

    let response = await fetch('/api/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            username: username.value,
            email: email.value,
            password: password.value
        })
    });
    if (response.status !== 200) return alert(`Error: ${(await response.json()).status}`);

    window.location.href = '/home';
});
