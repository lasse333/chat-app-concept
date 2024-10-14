export default async function App() {

    let username = window.localStorage.name ?? setName(prompt('What is your name?'))

    window.chat = await fetch('/api/chat/get_messages')
    window.chat = await window.chat.json()

    for (let message of window.chat.messages) {
        displayMessage(message, true)
    }

    window.chat_events = new EventSource('./api/chat/events?client_id=' + window.chat.client_id)

    window.chat_events.onmessage = function(event) {
        let message = JSON.parse(event.data)
        displayMessage(message)
    }

    

    document.querySelector(".message-input").onsubmit = function(event) {
        event.preventDefault()
        send_message(event.target.querySelector('input').value, username)
        event.target.querySelector('input').value = ''
    }
}

function send_message(message, username) {
    displayMessage({"content": message, "author": username}, true)
    fetch('/api/chat/send_message?client_id=' + window.chat.client_id, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            message: {"content": message, "author": username}
        })})
}

function setName(name) {
    window.localStorage.setItem('name', name)
    return name
}

function displayMessage(message, scroll = false) {
    console.log(message)
    let message_history = document.querySelector('.message-history')
    let is_at_bottom = message_history.scrollTop == message_history.scrollHeight-message_history.clientHeight

    while (message_history.childElementCount >= 100) {
        message_history.removeChild(message_history.firstChild)
    }

    let message_element = document.createElement('div')
    message_element.classList.add('message')

    let author = document.createElement("span")
    author.classList.add('author')
    author.innerHTML = message.author

    let content = document.createElement("span")
    content.classList.add('content')
    content.innerHTML = message.content

    message_element.appendChild(author)
    message_element.appendChild(content)
    message_history.appendChild(message_element)

    if (scroll || is_at_bottom) {
        message_history.scroll({top: message_history.scrollHeight-message_history.clientHeight, behavior: "instant"})
    }
}