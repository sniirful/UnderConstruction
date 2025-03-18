let sideUsername = document.querySelector('span#username');
let sideProfilePicture = document.querySelector('div#picture-container > img');

(async () => {
    let profile = await getProfile();

    sideUsername.innerText = profile.username;
    sideProfilePicture.src = profile.profile_picture ? `data:image/png;base64,${profile.profile_picture}` : `/src/profile.png`;
})();