// script.js

let userLocation = null;

// Elements
const chatBox = document.getElementById("chat-box");
const chatInput = document.getElementById("chat-input");
const sendBtn = document.getElementById("send-btn");
const locationStatus = document.getElementById("location-status");

// Request geolocation on page load
function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                userLocation = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                };
                locationStatus.textContent = "📍 Location detected. You can start chatting.";
            },
            (error) => {
                locationStatus.textContent = "⚠️ Please allow location to use Travel Assistant.";
            }
        );
    } else {
        locationStatus.textContent = "⚠️ Geolocation is not supported by your browser.";
    }
}

// Call on load
getLocation();

function appendMessage(message, sender="bot") {
    const div = document.createElement("div");
    div.classList.add("chat-message", sender);
    div.textContent = message;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

async function sendMessage() {
    const query = chatInput.value.trim();
    if (!query) return;

    appendMessage(query, "user");
    chatInput.value = "";

    if (!userLocation) {
        appendMessage("⚠️ Cannot get your location. Please allow location access.", "bot");
        return;
    }

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                query: query,
                lat: userLocation.lat,
                lng: userLocation.lng
            })
        });

        if (!response.ok) {
            appendMessage("⚠️ Error fetching response from server.", "bot");
            return;
        }

        const data = await response.json();
        appendMessage(data.text, "bot");
    } catch (err) {
        appendMessage("⚠️ Network error or server unavailable.", "bot");
    }
}

// Optional: press Enter to send
chatInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendMessage();
});

sendBtn.addEventListener("click", sendMessage);
