let postsContainer = document.querySelector('div.full');

async function refreshPosts() {
    let selectedFilters = Array.from(document.querySelectorAll('div.filters > div.selected > span')).map(span => span.textContent).join(',');
    let posts = (await (await fetch(`/api/posts/popular?genres=${selectedFilters}`)).json()).data;

    for (let post of document.querySelectorAll('div.post')) {
        post.remove();
    }
    for (let post of posts) {
        let {p, profilePicture, followButton, likeButton, commentButton, likesCommentsCount} = elements.create(`
            <div class="post" b-name="p">
                <div class="user-container">
                    <div class="picture-container">
                        <img b-name="profilePicture">
                    </div>
                    <div class="info-container">
                        <div class="top-row">
                            <span class="noto-sans">?</span>
                            <span class="bangers ${post.poster.following ? 'following' : ''}" b-name="followButton">${post.poster.following ? 'Unfollow' : 'Follow'}</span>
                        </div>
                        <div class="bottom-row">
                            <span class="noto-sans">${(() => {
            const now = Math.floor(Date.now() / 1000);
            const diff = now - post.posted;

            if (diff < 60) return `${diff}s`;
            else if (diff < 3600) return `${Math.floor(diff / 60)}m`;
            else if (diff < 86400) return `${Math.floor(diff / 3600)}h`;
            else if (diff < 2592000) return `${Math.floor(diff / 86400)}d`;
            else if (diff < 31536000) return `${Math.floor(diff / 2592000)}mo`;
            else return `${Math.floor(diff / 31536000)}y`;
        })()}</span>
                        </div>
                    </div>
                </div>
                <div class="text-container noto-sans">
                    ?
                </div>
                <div class="actions-container">
                    <div>
                        <button class="mini-button image ${post.liked ? 'liked' : ''}" b-name="likeButton">
                            <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960"
                                 width="24px" fill="#e3e3e3">
                                <path d="M720-120H280v-520l280-280 50 50q7 7 11.5 19t4.5 23v14l-44 174h258q32 0 56 24t24 56v80q0 7-2 15t-4 15L794-168q-9 20-30 34t-44 14Zm-360-80h360l120-280v-80H480l54-220-174 174v406Zm0-406v406-406Zm-80-34v80H160v360h120v80H80v-520h200Z"/>
                            </svg>
                            <span class="bangers">Like</span>
                        </button>
                        <button class="mini-button image" b-name="commentButton">
                            <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960"
                                 width="24px" fill="#e3e3e3">
                                <path d="M240-400h480v-80H240v80Zm0-120h480v-80H240v80Zm0-120h480v-80H240v80ZM880-80 720-240H160q-33 0-56.5-23.5T80-320v-480q0-33 23.5-56.5T160-880h640q33 0 56.5 23.5T880-800v720ZM160-320h594l46 45v-525H160v480Zm0 0v-480 480Z"/>
                            </svg>
                            <span class="bangers">Comment</span>
                        </button>
                    </div>
                    <div>
                        <span class="noto-sans" b-name="likesCommentsCount">Likes: ?, Comments: 0</span>
                    </div>
                </div>
            </div>
        `, post.poster.username, post.text, post.likes);

        followButton.addEventListener('click', async () => {
            if (followButton.classList.contains('following')) {
                const response = await fetch('/api/profile/unfollow', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({id: post.poster.id})
                });
                if (response.status === 200) {
                    followButton.classList.remove('following');
                    followButton.innerText = "Follow";
                } else {
                    alert(`Error: ${(await response.json()).status}`);
                }
            } else {
                const response = await fetch('/api/profile/follow', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({id: post.poster.id})
                });
                if (response.status === 200) {
                    followButton.classList.add('following');
                    followButton.innerText = "Unfollow";
                } else {
                    alert(`Error: ${(await response.json()).status}`);
                }
            }
        });

        // XSS-proof!
        profilePicture.src = post.poster.profile_picture ? `data:image/png;base64,${post.poster.profile_picture}` : `/src/profile.png`;

        likeButton.addEventListener('click', async () => {
            if (likeButton.classList.contains('liked')) {
                const response = await fetch('/api/posts/unlike', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({id: post.id})
                });
                if (response.status === 200) {
                    likeButton.classList.remove('liked');
                    likesCommentsCount.textContent = `Likes: ${post.likes - (!post.liked ? 0 : 1)}, Comments: 0`;
                } else {
                    alert(`Error: ${(await response.json()).status}`);
                }
            } else {
                const response = await fetch('/api/posts/like', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({id: post.id})
                });
                if (response.status === 200) {
                    likeButton.classList.add('liked');
                    likesCommentsCount.textContent = `Likes: ${post.likes + (post.liked ? 0 : 1)}, Comments: 0`;
                } else {
                    alert(`Error: ${(await response.json()).status}`);
                }
            }
        });

        commentButton.addEventListener('click', () => {
            alert('This feature is UnderConstruction.');
        });

        postsContainer.appendChild(p);
    }
}

refreshPosts();