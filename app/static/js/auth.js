async function login() {
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  const res = await fetch(
    `/api/v1/auth/login?username=${username}&password=${password}`,
    { method: "POST" }
  );

  const data = await res.json();

  if (!res.ok) {
  document.getElementById("error").innerText =
    data.detail || "Invalid username or password";
  return;
}

  localStorage.setItem("token", data.access_token);
  window.location.href = "/dashboard";
}
