/*
 * api.js
 * ------
 * Single shared wrapper around fetch() for calling the FastAPI backend.
 * Every page includes this file instead of writing its own fetch logic,
 * so there is exactly one place that knows the base URL, attaches the
 * JWT, and handles error responses consistently (no duplicate JS).
 */

const API_BASE_URL = "http://localhost:8000/api";

const Api = {
  token() {
    return localStorage.getItem("sb_token");
  },

  async request(method, path, body) {
    const headers = { "Content-Type": "application/json" };
    const token = this.token();
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const response = await fetch(`${API_BASE_URL}${path}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });

    let data = null;
    try {
      data = await response.json();
    } catch (e) {
      data = null;
    }

    if (!response.ok) {
      const message = (data && (data.detail || data.message)) || "Something went wrong. Please try again.";
      if (response.status === 401) {
        Auth.logout(false);
      }
      throw new Error(message);
    }
    return data;
  },

  get(path) { return this.request("GET", path); },
  post(path, body) { return this.request("POST", path, body); },
  put(path, body) { return this.request("PUT", path, body); },
};

const Auth = {
  saveSession(loginResponse) {
    localStorage.setItem("sb_token", loginResponse.access_token);
    localStorage.setItem("sb_role", loginResponse.role);
    localStorage.setItem("sb_name", loginResponse.full_name);
  },
  role() { return localStorage.getItem("sb_role"); },
  name() { return localStorage.getItem("sb_name"); },
  isLoggedIn() { return !!localStorage.getItem("sb_token"); },
  logout(redirect = true) {
    localStorage.removeItem("sb_token");
    localStorage.removeItem("sb_role");
    localStorage.removeItem("sb_name");
    if (redirect) window.location.href = "login.html";
  },
  /** Call at the top of every protected page. Redirects to login if not
   * authenticated, and redirects away if the role doesn't match. */
  guard(requiredRole) {
    if (!this.isLoggedIn()) {
      window.location.href = "login.html";
      return;
    }
    if (requiredRole && this.role() !== requiredRole) {
      window.location.href = this.dashboardForRole(this.role());
    }
  },
  dashboardForRole(role) {
    if (role === "CUSTOMER") return "customer_dashboard.html";
    if (role === "EMPLOYEE") return "employee_dashboard.html";
    if (role === "MANAGER") return "manager_dashboard.html";
    return "login.html";
  },
};

/** Small shared helper for showing success/error banners without
 * duplicating alert markup on every page. */
function showAlert(containerId, message, type = "danger") {
  const el = document.getElementById(containerId);
  if (!el) { alert(message); return; }
  el.innerHTML = `<div class="alert alert-${type} py-2" role="alert">${message}</div>`;
}

function formatCurrency(amount) {
  return "₹" + Number(amount).toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function formatDate(iso) {
  if (!iso) return "-";
  const d = new Date(iso);
  return d.toLocaleString("en-IN", { day: "2-digit", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" });
}
