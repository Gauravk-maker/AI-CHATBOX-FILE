// Change this if your backend runs on a different URL after deployment
const API_BASE = "http://127.0.0.1:5000/api";

const authScreen = document.getElementById("auth-screen");
const chatScreen = document.getElementById("chat-screen");
const authError = document.getElementById("auth-error");

const loginForm = document.getElementById("login-form");
const signupForm = document.getElementById("signup-form");
const showSignup = document.getElementById("show-signup");
const showLogin = document.getElementById("show-login");

const messagesEl = document.getElementById("messages");
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const welcomeUser = document.getElementById("welcome-user");
const logoutBtn = document.getElementById("logout-btn");
const clearBtn = document.getElementById("clear-btn");

// ---------- Helpers ----------
function showError(msg) {
  authError.textContent = msg;
}

function clearError() {
  authError.textContent = "";
}

function addMessage(role, text) {
  const div = document.createElement("div");
  div.className = `msg ${role}`;
  div.textContent = text;
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return div;
}

function showChatScreen(username) {
  authScreen.classList.add("hidden");
  chatScreen.classList.remove("hidden");
  welcomeUser.textContent = `Hi, ${username}`;
  loadHistory();
}

function showAuthScreen() {
  chatScreen.classList.add("hidden");
  authScreen.classList.remove("hidden");
  messagesEl.innerHTML = "";
}

// ---------- Auth screen toggle ----------
showSignup.addEventListener("click", (e) => {
  e.preventDefault();
  loginForm.classList.add("hidden");
  signupForm.classList.remove("hidden");
  showSignup.classList.add("hidden");
  showLogin.classList.remove("hidden");
  clearError();
});

showLogin.addEventListener("click", (e) => {
  e.preventDefault();
  signupForm.classList.add("hidden");
  loginForm.classList.remove("hidden");
  showLogin.classList.add("hidden");
  showSignup.classList.remove("hidden");
  clearError();
});

// ---------- Signup ----------
signupForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  clearError();

  const username = document.getElementById("signup-username").value.trim();
  const password = document.getElementById("signup-password").value;

  try {
    const res = await fetch(`${API_BASE}/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    const data = await res.json();

    if (!res.ok) {
      showError(data.error || "Signup failed");
      return;
    }

    // Auto-switch to login after successful signup
    showLogin.click();
    document.getElementById("login-username").value = username;
  } catch (err) {
    showError("Could not reach server. Is the backend running?");
  }
});

// ---------- Login ----------
loginForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  clearError();

  const username = document.getElementById("login-username").value.trim();
  const password = document.getElementById("login-password").value;

  try {
    const res = await fetch(`${API_BASE}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ username, password }),
    });
    const data = await res.json();

    if (!res.ok) {
      showError(data.error || "Login failed");
      return;
    }

    showChatScreen(data.username);
  } catch (err) {
    showError("Could not reach server. Is the backend running?");
  }
});

// ---------- Logout ----------
logoutBtn.addEventListener("click", async () => {
  await fetch(`${API_BASE}/logout`, { method: "POST", credentials: "include" });
  showAuthScreen();
});

// ---------- Clear history ----------
clearBtn.addEventListener("click", async () => {
  if (!confirm("Clear all chat history?")) return;
  await fetch(`${API_BASE}/history/clear`, { method: "POST", credentials: "include" });
  messagesEl.innerHTML = "";
});

// ---------- Load chat history on login ----------
async function loadHistory() {
  try {
    const res = await fetch(`${API_BASE}/history`, { credentials: "include" });
    const data = await res.json();
    messagesEl.innerHTML = "";
    (data.history || []).forEach((row) => addMessage(row.role, row.message));
  } catch (err) {
    console.error("Failed to load history", err);
  }
}

// ---------- Send chat message ----------
chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = chatInput.value.trim();
  if (!text) return;

  addMessage("user", text);
  chatInput.value = "";

  const loadingEl = addMessage("loading", "Thinking...");

  try {
    const res = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ message: text }),
    });
    const data = await res.json();

    loadingEl.remove();

    if (!res.ok) {
      addMessage("assistant", `Error: ${data.error || "Something went wrong"}`);
      return;
    }

    addMessage("assistant", data.reply);
  } catch (err) {
    loadingEl.remove();
    addMessage("assistant", "Error: Could not reach server.");
  }
});

// ---------- Check if already logged in (on page load) ----------
(async function checkSession() {
  try {
    const res = await fetch(`${API_BASE}/me`, { credentials: "include" });
    const data = await res.json();
    if (data.logged_in) {
      showChatScreen(data.username);
    }
  } catch (err) {
    // backend not reachable yet, stay on auth screen
  }
})();