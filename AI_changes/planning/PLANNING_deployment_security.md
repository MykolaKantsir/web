# PLANNING — Deployed Server Security Hardening

**Date raised:** 2026-07-31
**Status:** Planned / not yet done
**App:** Gaston Web (`gastoninternal`), Azure App Service, backed by Azure Database for PostgreSQL
**Scope:** production configuration only — no feature/behaviour changes

> Raised during a security review done for a *different* project (the Monitor G5
> voice assistant). While tracing how this app reaches Monitor data, the audit
> incidentally found production-config issues in this app worth fixing. This doc
> records the findings and the fix checklist; it does **not** change any code.

---

## Why this matters

The app is internet-reachable at `https://gastoninternal.azurewebsites.net`. The
issues below are low-drama on a private LAN but become real once an app is exposed
to the internet — which this one is. None of them are exploitable through the
app's *features*; they're all in how the deployment is configured.

---

## Findings (all in `web/web/settings.py`)

| # | Finding | Location | Why it's a problem |
|---|---------|----------|--------------------|
| 1 | **`DEBUG = True` in production** | `settings.py:28` | Django's debug pages show full stack traces, local variables, settings, and installed apps to **any visitor** who triggers an error. That is an information-disclosure hole (and can leak secrets that appear in tracebacks). Production must run `DEBUG = False`. |
| 2 | **`SECRET_KEY` hardcoded in source** | `settings.py:25` | The signing key for sessions, password-reset tokens, and CSRF is a literal in a file that lives in git. Anyone who can read the repo can forge sessions. It must come from an environment variable and never be committed. |
| 3 | **Database password (and host/user) hardcoded** | `settings.py:143-157` | The Azure PostgreSQL **password is in plaintext** in the source file (the `default` DB block). Same exposure as the secret key — repo read = DB credentials. Must move to environment variables / Azure App Settings. |
| 4 | **Web-push (VAPID) private key hardcoded** | `settings.py:203` | A private key committed to source. Move to env. |

Supporting context (not defects, just how it's deployed): served on Azure App
Service via GitHub Actions (`.github/workflows/main_gastoninternal.yml`), gunicorn
/ daphne + `web.config` FastCGI, WhiteNoise for static files, `ALLOWED_HOSTS`
already includes `gastoninternal.azurewebsites.net`. The data model is sound — the
app reads only the Azure Postgres DB (populated by the on-prem `update_watcher`);
it never reaches Monitor directly, so none of this touches Monitor security.

---

## Fix checklist (when scheduled)

1. **Move secrets to environment variables.** Read `SECRET_KEY`, the Postgres
   connection fields (`HOST`/`NAME`/`USER`/`PASSWORD`/`PORT`), and the web-push
   private key from `os.environ` (or `django-environ`). Keep a safe local-dev
   fallback only, and never a real secret as the default.
2. **`DEBUG = False`** in production — drive it from an env var
   (`DEBUG = os.environ.get("DJANGO_DEBUG", "") == "1"`), default off.
3. **Add the values to Azure** → App Service → *Configuration → Application
   settings*: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `POSTGRES_HOST`,
   `POSTGRES_NAME`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `WEBPUSH_PRIVATE_KEY`
   (names to match the settings refactor). App Settings are injected as env vars
   and are not in source control.
4. **Rotate the exposed secrets after they leave the source file** — the DB
   password, `SECRET_KEY`, and VAPID key have been sitting in a committed file, so
   treat them as compromised: change the Postgres password in Azure, generate a new
   Django `SECRET_KEY` (note: rotating it logs everyone out — expected), and
   regenerate the web-push keypair.
5. **Confirm** `ALLOWED_HOSTS` / `CSRF_TRUSTED_ORIGINS` still cover
   `gastoninternal.azurewebsites.net` after the refactor (they do today).
6. **Verify with `DEBUG=False`**: trigger an error and confirm you get a plain
   500 page (not the debug traceback), and that the app otherwise runs normally.

---

## Notes

- This is documentation only — no code was changed when this doc was written.
- The actual refactor is tracked as a separate work item.
- Cross-reference: the on-prem Monitor G5 voice-assistant project has its own,
  separate hardening plan (`D:\Projects\Voice-assistant\docs\remote-access-plan.md`).
