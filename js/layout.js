/*
 * layout.js
 * ---------
 * Renders the sidebar + topbar shell shared by every dashboard page,
 * per role. Keeping this in one file means the nav markup exists
 * exactly once in the whole project (no duplicate HTML/CSS across
 * 15 dashboard pages), and adding a new nav item means editing one
 * array instead of every page.
 */

const NAV_ITEMS = {
  CUSTOMER: [
    { href: "customer_dashboard.html", icon: "fa-gauge", label: "Dashboard" },
    { href: "accounts.html", icon: "fa-wallet", label: "Accounts" },
    { href: "deposit.html", icon: "fa-arrow-down", label: "Deposit" },
    { href: "withdraw.html", icon: "fa-arrow-up", label: "Withdraw" },
    { href: "transfer.html", icon: "fa-right-left", label: "Transfer" },
    { href: "transactions.html", icon: "fa-receipt", label: "Transactions" },
    { href: "loans.html", icon: "fa-hand-holding-dollar", label: "Loans" },
    { href: "notifications.html", icon: "fa-bell", label: "Notifications" },
    { href: "support.html", icon: "fa-headset", label: "Support" },
    { href: "profile.html", icon: "fa-user", label: "Profile" },
  ],
  EMPLOYEE: [
    { href: "employee_dashboard.html", icon: "fa-gauge", label: "Dashboard" },
    { href: "customers.html", icon: "fa-users", label: "Customers" },
    { href: "pending_accounts.html", icon: "fa-id-badge", label: "Pending Accounts" },
    { href: "transactions.html", icon: "fa-receipt", label: "All Transactions" },
    { href: "profile.html", icon: "fa-user", label: "Profile" },
  ],
  MANAGER: [
    { href: "manager_dashboard.html", icon: "fa-gauge", label: "Dashboard" },
    { href: "employees.html", icon: "fa-id-badge", label: "Employees" },
    { href: "customers.html", icon: "fa-users", label: "Customers" },
    { href: "accounts.html", icon: "fa-wallet", label: "All Accounts" },
    { href: "loans.html", icon: "fa-hand-holding-dollar", label: "Loans" },
    { href: "reports.html", icon: "fa-chart-line", label: "Reports" },
    { href: "audit_logs.html", icon: "fa-shield-halved", label: "Audit Logs" },
    { href: "branches.html", icon: "fa-code-branch", label: "Branches" },
    { href: "profile.html", icon: "fa-user", label: "Profile" },
  ],
};

const Layout = {
  init(requiredRole, activeHref) {
    Auth.guard(requiredRole);
    this.renderSidebar(requiredRole, activeHref);
    this.renderTopbar();
  },

  renderSidebar(role, activeHref) {
    const items = NAV_ITEMS[role] || [];
    const links = items.map(item => `
      <a href="${item.href}" class="nav-link ${item.href === activeHref ? "active" : ""}">
        <i class="fa-solid ${item.icon}"></i> ${item.label}
      </a>`).join("");

    const html = `
      <a href="index.html" class="brand-mark mb-4 d-block">
        <span class="brand-seal">S</span> Smart Digital Bank
      </a>
      <div class="nav-section-label">Menu</div>
      <nav class="nav flex-column">${links}</nav>
      <div class="mt-auto pt-4">
        <button class="nav-link w-100 text-start border-0 bg-transparent" onclick="Auth.logout()">
          <i class="fa-solid fa-right-from-bracket"></i> Log out
        </button>
      </div>
    `;
    const sidebarEl = document.getElementById("sbSidebar");
    if (sidebarEl) sidebarEl.innerHTML = html;
  },

  renderTopbar() {
    const roleLabels = { CUSTOMER: "Customer", EMPLOYEE: "Employee", MANAGER: "Manager" };
    const el = document.getElementById("sbTopbar");
    if (!el) return;
    el.innerHTML = `
      <button class="btn btn-outline-gold d-md-none" onclick="document.querySelector('.sidebar').classList.toggle('show')">
        <i class="fa-solid fa-bars"></i>
      </button>
      <div class="ms-auto d-flex align-items-center gap-3">
        <span class="text-muted-custom small">${roleLabels[Auth.role()] || ""}</span>
        <div class="d-flex align-items-center gap-2">
          <span class="brand-seal" style="width:34px;height:34px;font-size:0.9rem;">${(Auth.name() || "?").charAt(0).toUpperCase()}</span>
          <span class="fw-semibold">${Auth.name() || ""}</span>
        </div>
      </div>
    `;
  },
};
