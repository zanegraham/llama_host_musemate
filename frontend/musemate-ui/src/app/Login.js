"use client";
import { useState } from "react";

export default function Login({ onAuthSuccess }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!username || !password) {
      alert("Please enter both username and password");
      return;
    }

    setIsLoading(true);
    try {
      const res = await fetch("http://localhost:8000/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      const data = await res.json();
      
      if (res.ok) {
        localStorage.setItem("token", data.token);
        onAuthSuccess();
      } else {
        throw new Error(data.detail || "Login failed");
      }
    } catch (error) {
      console.error("Login error:", error);
      alert(error.message || "Login failed. Please try again.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="p-4 bg-black rounded-lg shadow">
      <h2 className="text-2xl mb-4">Login to MuseMate</h2>
      <input
        type="text"
        placeholder="Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        className="block w-full mb-2 p-2 border rounded"
        disabled={isLoading}
        required
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        className="block w-full mb-4 p-2 border rounded"
        disabled={isLoading}
        required
      />
      <button 
        type="submit"
        className="w-full p-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        disabled={isLoading}
      >
        {isLoading ? "Logging in..." : "Log In"}
      </button>
    </form>
  );
}