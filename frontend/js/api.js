/**
 * NexGen Hospital — API Client (FINAL STABLE VERSION)
 */

const API = (() => {

  // 🌐 BACKEND URL
  const BASE = "https://nexgen-hospital-app.onrender.com";

  // ================= TOKEN =================
  const token = () => localStorage.getItem("nexgen_token");

  const headers = () => ({
    "Content-Type": "application/json",
    ...(token() ? { Authorization: `Bearer ${token()}` } : {})
  });

  // ================= CORE REQUEST =================
  async function request(method, path, body) {
    try {
      const res = await fetch(`${BASE}${path}`, {
        method,
        headers: headers(),
        ...(body && { body: JSON.stringify(body) })
      });

      // 🔥 FIX: safely read response
      const text = await res.text();

      let data = {};
      try {
        data = text ? JSON.parse(text) : {};
      } catch {
        console.error("RAW RESPONSE:", text);
        throw new Error("Server error (invalid JSON)");
      }

      // 🔁 HANDLE UNAUTHORIZED
      if (res.status === 401) {
        logout();
        throw new Error("Session expired. Please login again.");
      }

      // ❌ HANDLE ERROR
      if (!res.ok) {
        throw new Error(data.detail || data.message || "Request failed");
      }

      return data;

    } catch (err) {
      console.error("API ERROR:", err);
      throw err;
    }
  }

  // ================= GENERIC =================
  const get   = (p)    => request("GET", p);
  const post  = (p, b) => request("POST", p, b);
  const put   = (p, b) => request("PUT", p, b);
  const patch = (p, b) => request("PATCH", p, b);
  const del   = (p)    => request("DELETE", p);

  // ================= AUTH =================
  async function login(username, password) {
    const res = await post("/api/auth/login", { username, password });

    // 🔥 FIX: flexible response handling
    const d = res.data || res;

    if (d.token || d.access_token) {

      const tokenVal = d.token || d.access_token;

      localStorage.setItem("nexgen_token", tokenVal);
      localStorage.setItem("nexgen_username", d.username || username);
      localStorage.setItem("nexgen_role", d.role || "ADMIN");
      localStorage.setItem("nexgen_name", d.fullName || "");

      return d;
    }

    throw new Error(res.message || "Login failed");
  }

  function logout() {
    [
      "nexgen_token",
      "nexgen_username",
      "nexgen_role",
      "nexgen_name"
    ].forEach(k => localStorage.removeItem(k));

    window.location.href = "login.html";
  }

  function getUser() {
    return {
      username: localStorage.getItem("nexgen_username"),
      role: localStorage.getItem("nexgen_role"),
      token: localStorage.getItem("nexgen_token")
    };
  }

  function requireRole(...roles) {
    const user = getUser();

    if (!user.token) {
      window.location.href = "login.html";
      return false;
    }

    // 🔥 FIX: normalize role
    const role = (user.role || "").toUpperCase();

    if (roles.length && !roles.map(r => r.toUpperCase()).includes(role)) {
      window.location.href = roleHome(role);
      return false;
    }

    return true;
  }

  function roleHome(role) {
    role = (role || "").toUpperCase();

    return role === "ADMIN"   ? "admin.html"
         : role === "DOCTOR"  ? "doctor.html"
         : role === "PATIENT" ? "patient.html"
         : "login.html";
  }

  // ================= ADMIN APIs =================
  async function createUser(data) {
    return await post("/api/admin/create-user", data);
  }

  async function deleteUser(username) {
    return await del(`/api/admin/user/${username}`);
  }

  async function updateUser(username, data) {
    return await put(`/api/admin/user/${username}`, data);
  }

  async function getPatients() {
    const res = await get("/api/admin/patients");
    return res.data || res || [];
  }

  async function addPatient(data) {
    return await post("/api/admin/patients", data);
  }

  async function getDoctors() {
    const res = await get("/api/admin/doctors");
    return res.data || res || [];
  }

  async function addDoctor(data) {
    return await post("/api/admin/doctors", data);
  }

  async function getAppointments() {
    const res = await get("/api/admin/appointments");
    return res.data || res || [];
  }

  async function addAppointment(data) {
    return await post("/api/admin/appointments", data);
  }

  async function getRecords() {
    const res = await get("/api/admin/records");
    return res.data || res || [];
  }

  async function getDashboard() {
    const res = await get("/api/admin/dashboard");
    return res.data || res || {};
  }

  // ================= AI APIs =================
  async function predictDisease(symptoms) {
    return await post("/api/ai/disease", { symptoms });
  }

  async function predictRisk(data) {
    return await post("/api/ai/risk", data);
  }

  async function predictICU(data) {
    return await post("/api/ai/icu", data);
  }

  async function chatbot(message) {
    return await post("/api/ai/chat", { message });
  }

  // ================= EXPORT =================
  return {
    get, post, put, patch, del,
    login, logout, getUser, requireRole, roleHome,

    // Admin
    createUser,
    deleteUser,
    updateUser,
    getPatients,
    addPatient,
    getDoctors,
    addDoctor,
    getAppointments,
    addAppointment,
    getRecords,
    getDashboard,

    // AI
    predictDisease,
    predictRisk,
    predictICU,
    chatbot
  };

})();


// ================= TOAST =================
function toast(msg, type = "success") {
  const colors = {
    success: "#00e5a0",
    error: "#ff4757",
    info: "#00d4ff"
  };

  const el = document.createElement("div");

  el.style = `
    position:fixed;
    bottom:20px;
    right:20px;
    background:#0b1120;
    border-left:4px solid ${colors[type]};
    color:white;
    padding:12px 18px;
    border-radius:8px;
    z-index:9999;
  `;

  el.textContent = msg;
  document.body.appendChild(el);

  setTimeout(() => el.remove(), 3000);
}
