# Security Rules

Priority: CRITICAL

---

Validate everything.

Trust nothing.

---

Uploads

Allowed

PDF

DOCX

TXT

Reject

Executables

Archives

Unknown MIME types

---

Limits

Max upload size configurable.

Reject oversized files.

---

Authentication

JWT

OAuth (future)

Sessions not allowed.

---

Authorization

Always check ownership.

Never trust frontend permissions.

---

Secrets

Read only from environment.

Never hardcode.

Never commit.

---

Prompt Injection

Treat uploaded resumes as untrusted.

Treat job descriptions as untrusted.

Never execute model output.

Validate structured outputs.

---

SQL Injection

Always parameterized queries.

---

XSS

Escape rendered HTML.

Sanitize Markdown.

---

Dependencies

Keep packages updated.

Review CVEs regularly.

---

Headers

Security headers enabled.

HTTPS required in production.

CORS explicitly configured.

---

Logging

Never log sensitive information.
