let mainContainer = document.querySelector('main');

let infoUsername = document.querySelector('span#info-username');
let infoEmail = document.querySelector('span#info-email');
let infoFavoriteManga = document.querySelector('span#info-fav-manga');
let infoFavoriteGenres = document.querySelector('span#info-fav-genres');

let buttonChangeManga = document.querySelector('span#info-fav-manga + div.mini-button');
let buttonChangeGenres = document.querySelector('span#info-fav-genres + div.mini-button');
let buttonChangeProfilePicture = document.querySelector('button.button.image');

(async () => {
    let isAdmin = (await getProfile()).username === 'admin';
    let profile = new URL(window.location.href).searchParams.get('id')
        ? await getProfileById(new URL(window.location.href).searchParams.get('id'))
        : await getProfile();

    if (isAdmin) {
        let {divider, warning, textarea, changeCSSButton} = elements.create(`
            <div b-name="divider" class="divider"></div>
            <h3 b-name="warning" class="bangers">Warning! Experimental feature</h3>
            <textarea b-name="textarea" name="css" placeholder="Enter CSS for the profile here..."></textarea>
            <button b-name="changeCSSButton" id="change-css-button" class="button image">
                <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e3e3e3">
                    <path d="M320-240 80-480l240-240 57 57-184 184 183 183-56 56Zm320 0-57-57 184-184-183-183 56-56 240 240-240 240Z"/>
                </svg>
                <span class="bangers">Change CSS</span>
            </button>
        `);

        changeCSSButton.addEventListener('click', async () => {
            let response = await fetch('/api/profile/css', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    id: profile.id,
                    css: textarea.value
                })
            });
            if (response.status !== 200) return alert(`Error: ${(await response.json()).status}`);

            window.location.reload();
        });

        mainContainer.appendChild(divider);
        mainContainer.appendChild(warning);
        mainContainer.appendChild(textarea);
        mainContainer.appendChild(changeCSSButton);
    }

    infoUsername.innerText = profile.username;
    infoEmail.innerText = profile.email;
    infoFavoriteManga.innerText = profile.fav_manga;
    infoFavoriteGenres.innerText = profile.fav_genres.join(', ');

    buttonChangeManga.addEventListener('click', async () => {
        let newManga = prompt('Type in the the new manga you like more!', profile.fav_manga);

        let response = await fetch('/api/profile/manga', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                fav_manga: newManga
            })
        });
        if (response.status !== 200) return alert(`Error: ${(await response.json()).status}`);

        window.location.reload();
    });

    buttonChangeGenres.addEventListener('click', async () => {
        let newGenres = prompt(
            'Type in the the new genres you like, separated by a comma!',
            profile.fav_genres.join(', ')
        ).split(',').map(genre => genre.trim());

        let response = await fetch('/api/profile/genres', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                fav_genres: newGenres
            })
        });
        if (response.status !== 200) return alert(`Error: ${(await response.json()).status}`);

        window.location.reload();
    });

    buttonChangeProfilePicture.addEventListener('click', async () => {
        let fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = 'image/*';
        fileInput.onchange = async () => {
            let file = fileInput.files[0];
            if (file) {
                let reader = new FileReader();
                reader.onload = async (e) => {
                    let base64Image = e.target.result.split(',')[1];
                    let response = await fetch('/api/profile/picture', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            profile_picture: base64Image
                        })
                    });
                    if (response.status !== 200) return alert(`Error: ${(await response.json()).status}`);
                    window.location.reload();
                };
                reader.readAsDataURL(file);
            }
        };
        fileInput.click();
    });

    if (profile.css) {
        // Will not escape it or else the CSS will get escaped too...
        let {newStyle} = elements.create(`
            <style b-name="newStyle">
                ${profile.css}
            </style>
        `);
        document.head.appendChild(newStyle);
    }
})();