// -------------------------------------------------
// LOGOUT
// -------------------------------------------------
async function logout() {
  await fetch("/api/v1/auth/logout", {
    method: "POST",
    credentials: "include"
  });

  window.location.href = "/";
}

// -------------------------------------------------
// LOAD DOMAINS
// -------------------------------------------------
async function loadDomains() {
  const res = await fetch("/api/v1/domains", {
    credentials: "include"
  });

  if (!res.ok) return;

  const domains = await res.json();
  const list = document.getElementById("domains");
  list.innerHTML = "";

  domains.forEach(d => {
    const li = document.createElement("li");
    li.innerText = `${d.name} (${d.provider})`;
    list.appendChild(li);
  });
}

// -------------------------------------------------
// LOAD EMAILS
// -------------------------------------------------
async function loadEmails() {
  const res = await fetch("/api/v1/emails", {
    credentials: "include"
  });

  if (!res.ok) return;

  const emails = await res.json();
  const list = document.getElementById("emails");
  list.innerHTML = "";

  emails.forEach(e => {
    let statusClass = "status-pending";
    if (e.status === "active") statusClass = "status-active";
    if (e.status === "disabled") statusClass = "status-disabled";

    const li = document.createElement("li");
    li.innerHTML = `
      <span>
        ${e.email} —
        <span class="${statusClass}">${e.status}</span>
      </span>
      <span>
        <button class="success" onclick="activateEmail('${e.email}')">Activate</button>
        <button class="danger" onclick="deactivateEmail('${e.email}')">Deactivate</button>
      </span>
    `;
    list.appendChild(li);
  });
}

// -------------------------------------------------
// CREATE EMAIL
// -------------------------------------------------
async function createEmail() {
  const domain = document.getElementById("domain").value;
  const localPart = document.getElementById("localPart").value;
  const msg = document.getElementById("createMsg");

  msg.innerText = "Creating...";

  const res = await fetch(
    `/api/v1/emails/create?domain=${domain}&local_part=${localPart}`,
    {
      method: "POST",
      credentials: "include"
    }
  );

  const data = await res.json();

  if (!res.ok) {
    msg.innerText = data.detail || "Failed to create email";
    return;
  }

  msg.innerText = `Created: ${data.email} (${data.status})`;
  document.getElementById("domain").value = "";
  document.getElementById("localPart").value = "";

  loadEmails();
  loadDomains();
}

// -------------------------------------------------
// ACTIVATE / DEACTIVATE
// -------------------------------------------------
async function activateEmail(email) {
  await fetch(`/api/v1/emails/activate?email=${email}`, {
    method: "POST",
    credentials: "include"
  });
  loadEmails();
}

async function deactivateEmail(email) {
  await fetch(`/api/v1/emails/deactivate?email=${email}`, {
    method: "POST",
    credentials: "include"
  });
  loadEmails();
}

// -------------------------------------------------
// INIT
// -------------------------------------------------
loadDomains();
loadEmails();