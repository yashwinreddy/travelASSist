let userLocation = null;

// On page load → request geolocation
window.onload = function () {
  requestLocation();
};

function requestLocation() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        userLocation = {
          lat: position.coords.latitude,
          lng: position.coords.longitude,
        };
        document.getElementById("location-status").innerText =
          "✅ Location enabled. You can start asking queries.";
      },
      (error) => {
        document.getElementById("location-status").innerText =
          "❌ Location access blocked. Please allow location to use this app.";
        // Keep retrying every 3 seconds
        setTimeout(requestLocation, 3000);
      }
    );
  } else {
    alert("Geolocation is not supported by your browser.");
  }
}

// Add user message to chat box
function addMessage(text, sender = "user") {
  const chatBox = document.getElementById("chat-box");
  const msg = document.createElement("div");
  msg.classList.add("message");
  msg.classList.add(sender === "user" ? "user-message" : "bot-message");
  msg.innerText = text;
  chatBox.appendChild(msg);
  chatBox.scrollTop = chatBox.scrollHeight; // auto-scroll
}

// Send query to backend
async function sendMessage() {
  const input = document.getElementById("chat-input");
  const query = input.value.trim();

  if (!query) return;
  if (!userLocation) {
    addMessage("Please allow location access before asking.", "bot");
    return;
  }

  // Show user message
  addMessage(query, "user");
  input.value = "";

  try {
    const response = await fetch(
      `/route-info?origin_lat=${userLocation.lat}&origin_lng=${userLocation.lng}&destination=${encodeURIComponent(
        query
      )}`
    );

    const data = await response.json();

    if (data.source === "cache") {
      addMessage("⚡ (cached data)", "bot");
    }

    // Format bot response
    let reply = `📍 Route info from ${data.origin} to ${data.destination}\n\n`;

    for (const mode in data.routes) {
      const r = data.routes[mode];
      if (r.error) {
        reply += `❌ ${mode}: ${r.error}\n`;
      } else {
        reply += `🚗 ${mode}: ${r.distance}, ${r.duration}`;
        if (r.traffic) reply += ` (${r.traffic})`;
        if (r.alternates && r.alternates.length > 0) {
          reply += `\n   🔀 Alternates: ${r.alternates.join(" | ")}`;
        }
        reply += `\n`;
      }
    }

    reply += `\n🌦 Weather at destination: ${data.weather.status}, ${data.weather.temperature}`;

    addMessage(reply, "bot");
  } catch (error) {
    addMessage("⚠️ Error fetching route info. Try again.", "bot");
  }
}
