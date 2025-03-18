let main = document.querySelector('main');

let fullChatsContainer = document.querySelector('main > div.full');
let fullChatsContainerChild = document.querySelector('main > div.full > div.divider');

async function checkChats() {
    let response = await fetch(`/api/chats`);
    if (response.status !== 200) return;

    let chatsList = await response.json();
    if (chatsList.length <= 0) {
        main.className = 'empty';
        return;
    }

    for (let chatElement of document.querySelectorAll('div.full > div.chat')) chatElement.remove();
    for (let chat of chatsList) {
        let {chatElement, profilePicture} = elements.create(`
            <div class="chat" b-name="chatElement">
                <div class="profile-picture">
                    <img src="/src/profile.png" b-name="profilePicture">
                </div>
                <div class="container">
                    <span class="username noto-sans">?</span>
                    <span class="last-message noto-sans">?</span>
                </div>
            </div>
        `, chat.username, chat.message);

        chatElement.addEventListener('click', () => {
            openChat(`${chat.recipient}`);
        });

        profilePicture.src = chat.profile_picture ? `data:image/png;base64,${chat.profile_picture}` : `/src/profile.png`;
        fullChatsContainer.insertBefore(chatElement, fullChatsContainerChild.nextSibling);
    }
    main.className = 'full';
}

let startNewChatButtons = document.querySelectorAll('.start-new-chat');
for (let button of startNewChatButtons) button.addEventListener('click', e => {
    e.preventDefault();

    let id = prompt('Enter the ID of the recipient');
    if (id === '') return;

    openChat(id);
});

let chatProfilePictureElement = document.querySelector('div.chat > div.user-info > div.user-profile-picture > img');
let chatBackButton = document.querySelector('div.chat > div.user-info > div.button');
let chatUsernameElement = document.querySelector('div.chat > div.user-info > span');
let textarea = document.querySelector('textarea');
let postButton = document.querySelector('div#post-button');
let messagesContainer = document.querySelector('div.actual-chat');
let messagesContainerChild = document.querySelector('div.actual-chat > div.text-container');

async function openChat(id) {
    let response = await fetch(`/api/chats/user?id=${encodeURI(id)}`);
    if (response.status !== 200) return;

    let userInfo = await response.json();

    response = await fetch(`/api/chats/messages?id=${encodeURI(id)}`);
    if (response.status !== 200) return;

    let messages = await response.json();

    chatProfilePictureElement.src = userInfo.profile_picture ? `data:image/png;base64,${userInfo.profile_picture}` : `/src/profile.png`;
    chatUsernameElement.innerText = userInfo.username;

    for (let message of document.querySelectorAll('div.message')) message.remove();
    for (let message of messages) {
        let {messageElement} = elements.create(`
            <div class="message ${(message['to_id'].toString() === id) ? ('sent') : ('received')}" b-name="messageElement">
                <div class="bubble">
                    <div class="text noto-sans">
                        ?
                    </div>
                    <div class="time noto-sans">${new Date(message.sent * 1000).toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit'
        })}</div>
                </div>
            </div>
        `, message['message']);

        messagesContainer.insertBefore(messageElement, messagesContainerChild.nextSibling);
    }

    let socket = io();

    socket.on('connect', () => {
        socket.emit('room', id);
    });

    socket.on('message', data => {
        let {messageElement} = elements.create(`
            <div class="message received" b-name="messageElement">
                <div class="bubble">
                    <div class="text noto-sans">
                        ?
                    </div>
                    <div class="time noto-sans">${new Date(data.sent * 1000).toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit'
        })}</div>
                </div>
            </div>
        `, data.message);
        messagesContainer.insertBefore(messageElement, messagesContainerChild.nextSibling);
    });

    postButton.onclick = () => {
        socket.emit('message', parseInt(id), textarea.value);

        let {messageElement} = elements.create(`
            <div class="message sent" b-name="messageElement">
                <div class="bubble">
                    <div class="text noto-sans">
                        ?
                    </div>
                    <div class="time noto-sans">${new Date().toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit'
        })}</div>
                </div>
            </div>
        `, textarea.value);

        messagesContainer.insertBefore(messageElement, messagesContainerChild.nextSibling);

        textarea.value = '';
    };
    chatBackButton.onclick = () => {
        socket.close();
        checkChats();
    };

    main.className = 'chat';
}

document.querySelector('#add-picture-button').addEventListener('click', () => {
    alert('This feature is UnderConstruction.');
});

checkChats();