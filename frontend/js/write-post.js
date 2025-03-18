const textarea = document.querySelector('textarea#post-text');
const textareaImageButton = document.querySelector('div#add-picture-button');
const postButton = document.querySelector('div#post-button');

function resizeTextarea() {
    textarea.style.height = 'auto';
    textarea.style.height = (textarea.scrollHeight) + 'px';
}

textarea.addEventListener('input', resizeTextarea);
document.addEventListener('DOMContentLoaded', resizeTextarea);

textareaImageButton.addEventListener('click', () => {
    alert('This feature is UnderConstruction.');
});
postButton.addEventListener('click', async () => {
    const response = await fetch('/api/post', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text: textarea.value })
    });

    if (response.status === 200) {
        alert('Post published.');
        textarea.value = '';
        resizeTextarea();
    } else {
        alert(`Error: ${(await response.json()).status}`);
    }
});