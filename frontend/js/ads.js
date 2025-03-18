document.addEventListener('DOMContentLoaded', async () => {
    let profile = await getProfile();
    if (profile.username === 'admin') return;

    for (let adElement of document.querySelectorAll('div.ad')) {
        let response = await fetch('/ad');
        if (response.status !== 200) continue;

        let data = await response.json();
        adElement.querySelector('a').href = data.link;
        adElement.querySelector('img').src = `data:image/png;base64,${data.image}`;
    }
});