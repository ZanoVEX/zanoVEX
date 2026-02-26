async function login() {
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  const formData = new FormData();
  formData.append("username", username);
  formData.append("password", password);

  const res = await fetch("/api/v1/auth/login", {
    method: "POST",
    body: formData
  });

  const data = await res.json();

  if (!res.ok) {
    document.getElementById("error").innerText =
      data.detail || "Invalid username or password";
    return;
  }

  localStorage.setItem("token", data.access_token);
  window.location.href = "/dashboard";
}