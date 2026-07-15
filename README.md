# Smart Digital Banking Platform

A full-stack banking application built to demonstrate **production-style software
engineering** — clean architecture, the Repository + Service Layer patterns, and
every core Object-Oriented Programming concept, implemented where it naturally
solves a real problem (never forced in just to tick a box).

- **Frontend:** HTML5, CSS3, Bootstrap 5, vanilla JavaScript
- **Backend:** Python, FastAPI
- **Database:** MySQL only (via SQLAlchemy ORM)
- **Auth:** JWT + bcrypt password hashing + email OTP + Role-Based Access Control

> This has been built and tested end-to-end against a real local MySQL database —
> register → OTP → login → open account → employee approval → deposit → withdraw →
> transfer → loans → manager operations all work. See `docs/OOP_CONCEPTS.md` for
> the interview-ready explanation of every OOP concept in this codebase.

---

## 1. Project structure

```
Banking/
  index.html, login.html, register.html, forgot_password.html
  customer_dashboard.html, accounts.html, deposit.html, withdraw.html,
  transfer.html, transactions.html, loans.html, notifications.html,
  support.html, profile.html
  employee_dashboard.html, customers.html, pending_accounts.html
  manager_dashboard.html, employees.html, reports.html, audit_logs.html, branches.html
  css/style.css
  js/api.js         <- shared fetch wrapper + auth/session helpers
  js/layout.js       <- shared sidebar/topbar renderer (per role)
  database/schema.sql
  backend/
    requirements.txt
    .env.example
    create_first_manager.py
    app/
      main.py, config.py, database.py
      core/          <- exceptions.py, security.py, dependencies.py (RBAC)
      models/        <- ORM models (*_orm.py) AND the OOP domain layer
      schemas/       <- Pydantic request/response models
      repositories/  <- Repository Pattern (all SQL lives here)
      services/      <- Service Layer (business logic / orchestration)
      routers/       <- FastAPI endpoints, grouped by role
  docs/
    OOP_CONCEPTS.md  <- maps every OOP concept to exact files/classes
```

## 2. Setting up MySQL (MySQL Workbench)

1. Open MySQL Workbench and connect to your local MySQL server.
2. Open `database/schema.sql` and execute it (⚡ button). This creates the
   `smart_banking` database and all 13 tables.
3. Note your MySQL root password — you'll need it in the next step.

## 3. Setting up the backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# edit .env: set DB_PASSWORD to your MySQL root password
```

Create the first Manager login (managers can't self-register, so you bootstrap one):

```bash
python create_first_manager.py
# Full name: Priya Sharma
# Email: manager@example.com
# Password: manager123
```

Run the API:

```bash
uvicorn app.main:app --reload --port 8000
```

Visit `http://localhost:8000/docs` for the interactive Swagger UI (every endpoint,
try-it-out included).

## 4. Setting up the frontend

The frontend is plain static HTML/CSS/JS — no build step. From the `Banking/`
folder:

```bash
python -m http.server 5500
```

Then open `http://localhost:5500/index.html` in your browser.

> `js/api.js` points at `http://localhost:8000/api` by default. If you run the
> backend on a different host/port, change `API_BASE_URL` at the top of that file.

## 5. Walking through the app

1. **Register** a customer on `register.html` → an OTP is generated.
   In local dev (no SMTP configured), the OTP is printed to your **backend
   terminal/console** instead of emailed — look for a block that says
   `[DEV MODE - OTP EMAIL NOT ACTUALLY SENT]`.
2. **Verify** the OTP, then **log in**.
3. On the customer dashboard, **open an account** (Savings/Current/Student).
4. Log in as the **Manager** you bootstrapped, go to **Employees**, create an
   employee.
5. Log in as that **Employee**, go to **Pending Accounts**, approve the
   customer's account.
6. Back as the **Customer**: deposit, withdraw, transfer, apply for a loan.
7. Back as the **Manager**: approve/reject the loan, freeze/activate accounts,
   view reports and audit logs.

## 6. Configuring real email (optional)

By default OTPs print to the console so you can develop without a mailbox.
To send real emails, set `SMTP_USERNAME` / `SMTP_PASSWORD` in `backend/.env`
(e.g. a Gmail account with an App Password). See `backend/app/utils/email_otp.py`.

## 7. What's fully built vs. scaffolded

**Fully working, tested against real MySQL:** registration, email OTP
verification, login, forgot/reset password, change password, RBAC across all
three roles, opening accounts, employee approval, deposit, withdraw, transfer
(with per-account-type business rules enforced), transaction history + search,
loan application + manager approval, manager creating employees, freeze/activate
accounts, branches, audit logs, reports, notifications, support tickets.

**Scaffolded for you to extend the same way (tables + basic wiring exist,
extend the same repository → service → router pattern):** debit cards, richer
notification triggers (e.g. auto-notify on loan decisions), CSV/PDF report
exports.

## 8. Adding a new feature (the pattern to follow)

Every feature in this app follows the same four-file pattern. To add a new one:

1. **ORM model** (`models/*_orm.py`) — the MySQL table shape.
2. **Repository** (`repositories/*.py`) — raw queries only.
3. **Service** (`services/*.py`) — business rules, calls the repository.
4. **Router** (`routers/*.py`) — HTTP endpoint, calls the service.

This is exactly what the Repository Pattern + Service Layer buy you: each
layer has one job, and you can explain that separation in an interview using
your own code.
