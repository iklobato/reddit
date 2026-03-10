# iktech.solutions – Email & Mailbox Checklist

## Script results (automated check)

- **iktech.solutions**: MX records present → email is configured (GoDaddy Workspace).
  - MX: smtp.secureserver.net (0), mailstore1.secureserver.net (10).
  - Both resolve to GoDaddy IPs.
- **iktech.dev**: No MX records → email not configured.

SMTP port reachability from this network was not possible (common on restricted networks); that does not mean your mail server is down.

---

## Confirm a mailbox works (e.g. contact@iktech.solutions)

### 1. Verify the mailbox exists in GoDaddy

1. Go to [GoDaddy](https://www.godaddy.com) and sign in.
2. **My Products** → find **iktech.solutions**.
3. Click **Manage** (or **DNS** / **Email**).
4. Open **Workspace Email** or **Email** (the product that uses secureserver.net).
5. Check the **user/mailbox list**. Ensure a mailbox named **contact** exists (so the address is contact@iktech.solutions).
6. If it does not exist: create it and set a password. If you don’t see “Workspace Email” or “Email”, you may need to add the product for this domain.

### 2. Test in webmail

1. Go to [https://webmail.secureserver.net](https://webmail.secureserver.net).
2. Log in with:
   - **Email:** contact@iktech.solutions  
   - **Password:** the mailbox password from step 1.
3. Send a test message to another address and check that you can receive a reply. If both work, the mailbox is working.

### 3. Use in a mail client (optional)

- **Incoming (IMAP):** server `imap.secureserver.net`, port **993** (SSL).  
- **Outgoing (SMTP):** server `smtp.secureserver.net`, port **465** (SSL) or **587** (TLS).  
- **Username:** contact@iktech.solutions (full address).  
- **Password:** same mailbox password.

---

## Run the check again

```bash
python3 check_domain_email.py iktech.solutions contact@iktech.solutions
python3 check_domain_email.py iktech.dev
```
