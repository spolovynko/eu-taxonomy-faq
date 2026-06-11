const conversation = document.getElementById("conversation");
const chatForm = document.getElementById("chatForm");
const messageInput = document.getElementById("messageInput");
const sendButton = document.getElementById("sendButton");
const clearChatButton = document.getElementById("clearChat");

const demoResponses = new Map([
    [
        "Which activities are Taxonomy-eligible?",
        "An activity is Taxonomy-eligible when it is described in the EU Taxonomy Delegated Acts, regardless of whether it already meets every technical screening criterion. Eligibility is the first step; alignment requires substantial contribution, DNSH and minimum safeguards checks.",
    ],
    [
        "Explain substantial contribution in simple terms.",
        "Substantial contribution means an economic activity makes a meaningful positive contribution to at least one of the EU's six environmental objectives and meets the relevant technical screening criteria for that objective.",
    ],
    [
        "What does do no significant harm mean?",
        "Do no significant harm, or DNSH, means an activity contributing to one environmental objective must not materially undermine any of the other five objectives. The applicable criteria depend on the activity and delegated act.",
    ],
]);

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

function getDemoResponse(question) {
    return demoResponses.get(question)
        || "This frontend is ready for an EU Taxonomy chat service. Connect the form handler in app.js to your API endpoint to replace this illustrative response with live answers.";
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

    await new Promise((resolve) => window.setTimeout(resolve, 650));

    if (requestSequence !== responseSequence) {
        return;
    }

    typingMessage.remove();
    createMessage("assistant", getDemoResponse(question));
    messageInput.disabled = false;
    updateSendState();
    messageInput.focus();
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
