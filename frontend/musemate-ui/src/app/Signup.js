"use client";

import { useState } from "react";

export default function Signup({ onAuthSuccess }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  async function handleSignup() {
    const res = await fetch("http://localhost:8000/signup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    if (res.ok) {
      alert("Account created! You can now log in.");
    } else {
      alert("Signup failed: " + (await res.json()).detail);
    }
  }

  return (
    <div>
      <h2>Signup</h2>
      <input placeholder="Username" value={username} onChange={e => setUsername(e.target.value)} />
      <input placeholder="Password" type="password" value={password} onChange={e => setPassword(e.target.value)} />
      <button onClick={handleSignup}>Sign Up</button>
    </div>
  );
}
