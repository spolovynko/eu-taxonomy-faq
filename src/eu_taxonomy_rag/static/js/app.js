const conversation = document.getElementById("conversation");
const chatForm = document.getElementById("chatForm");
const messageInput = document.getElementById("messageInput");
const sendButton = document.getElementById("sendButton");
const clearChatButton = document.getElementById("clearChat");

let responseSequence = 0;

function resizeInput() {
    messageInput.style.height = "auto";
    messageInput.style.height = `${Math.min(messageInput.scrollHeight, 140)}px`;
}

function updateSendState() {
    const hasContent = messageInput.value.trim().length > 0;
    sendButton.disabled = !hasContent || messageInput.disabled;
}

function scrollToLatest() {
    conversation.scrollTop = conversation.scrollHeight;
}

function createMessage(role, text, options = {}) {
    const message = document.createElement("article");
    message.className = `message message--${role}`;

    const avatar = document.createElement("div");
    avatar.className = "message__avatar";
    avatar.setAttribute("aria-hidden", "true");
    avatar.textContent = role === "assistant" ? "EU" : "YOU";

    const content = document.createElement("div");
    content.className = "message__content";

    const label = document.createElement("p");
    label.className = "message__label";
    label.textContent = role === "assistant" ? "Taxonomy assistant" : "You";

    const bubble = document.createElement("div");
    bubble.className = "message__bubble";

    if (options.typing) {
        const typing = document.createElement("div");
        typing.className = "typing-indicator";
        typing.setAttribute("aria-label", "Assistant is typing");
        typing.innerHTML = "<span></span><span></span><span></span>";
        bubble.appendChild(typing);
    } else {
        bubble.textContent = text;
    }

    content.append(label, bubble);
    message.append(avatar, content);
    conversation.appendChild(message);
    scrollToLatest();
    return message;
}

async function streamAnswer(question, onChunk) {
    const response = await fetch("/api/chat/stream", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ question }),
    });

    if (!response.ok) {
        throw new Error("The assistant could not answer the question.");
    }

    if (!response.body) {
        throw new Error("Streaming is not supported by this browser.");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
        const { value, done } = await reader.read();

        if (done) {
            break;
        }

        onChunk(decoder.decode(value, { stream: true }));
    }

    const remainingText = decoder.decode();
    if (remainingText) {
        onChunk(remainingText);
    }
}

async function handleSubmit(event) {
    event.preventDefault();

    const question = messageInput.value.trim();
    if (!question) {
        return;
    }

    createMessage("user", question);
    messageInput.value = "";
    resizeInput();

    messageInput.disabled = true;
    updateSendState();
    clearChatButton.disabled = false;

    const requestSequence = ++responseSequence;
    const typingMessage = createMessage("assistant", "", { typing: true });
    let answerBubble = null;

    try {
        await streamAnswer(question, (chunk) => {
            if (requestSequence === responseSequence) {
                if (!answerBubble) {
                    typingMessage.remove();
                    const assistantMessage = createMessage("assistant", "");
                    answerBubble = assistantMessage.querySelector(".message__bubble");
                }

                answerBubble.textContent += chunk;
                scrollToLatest();
            }
        });

        if (!answerBubble) {
            throw new Error("The assistant returned an empty response.");
        }
    } catch (error) {
        if (requestSequence === responseSequence) {
            typingMessage.remove();

            if (answerBubble) {
                answerBubble.textContent += "\n\nThe response was interrupted.";
            } else {
                createMessage("assistant", error.message);
            }
        }
    } finally {
        if (requestSequence === responseSequence) {
            messageInput.disabled = false;
            updateSendState();
            messageInput.focus();
        }
    }
}

function clearConversation() {
    responseSequence += 1;
    conversation.querySelectorAll(".message").forEach((message) => message.remove());
    messageInput.value = "";
    messageInput.disabled = false;
    clearChatButton.disabled = true;
    resizeInput();
    updateSendState();
    messageInput.focus();
}

chatForm.addEventListener("submit", handleSubmit);

messageInput.addEventListener("input", () => {
    resizeInput();
    updateSendState();
});

messageInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        chatForm.requestSubmit();
    }
});

clearChatButton.addEventListener("click", clearConversation);

resizeInput();
updateSendState();
