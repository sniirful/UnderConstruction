async function getProfile() {
    return new Promise(async resolve => {
        let response = await fetch('/api/profile');
        // return resolve(response.status === 200, await response.json());
        return resolve(response.status === 200 ? (await response.json()).data : null);
    });
}

async function getProfileById(id) {
    return new Promise(async resolve => {
        let response = await fetch(`/api/profile?id=${id}`);
        // return resolve(response.status === 200, await response.json());
        return resolve(response.status === 200 ? (await response.json()).data : null);
    });
}

async function checkLoginAndRedirect() {
    window.location.href = (await getProfile() ? '/home' : '/login');
}

async function checkLoginAndRedirectToHome() {
    if (await getProfile()) window.location.href = '/home';
}

async function checkLoginAndRedirectToLogin() {
    if (!await getProfile()) window.location.href = '/login';
}
