"use client";

import { useState } from "react";

export default function Login({ onAuthSuccess }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  async function handleLogin() {
    const res = await fetch("http://localhost:8000/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    if (res.ok) {
      const data = await res.json();
      localStorage.setItem("token", data.token);
      onAuthSuccess(); // tells main app that login worked
    } else {
      alert("Login failed: " + (await res.json()).detail);
    }
  }

  return (
    <div>
      <h2>Login</h2>
      <input placeholder="Username" value={username} onChange={e => setUsername(e.target.value)} />
      <input placeholder="Password" type="password" value={password} onChange={e => setPassword(e.target.value)} />
      <button onClick={handleLogin}>Log In</button>
    </div>
  );
}
