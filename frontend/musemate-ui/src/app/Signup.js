"use client";
import { useState } from "react";

export default function Signup({ onAuthSuccess }) {
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
      // Test backend connection first
      const testConnection = await fetch("http://localhost:8000/");
      if (!testConnection.ok) {
        throw new Error("Backend server not responding");
      }

      console.log("Creating account...");
      const signupRes = await fetch("http://localhost:8000/signup", {
        method: "POST",
        headers: { 
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ username, password }),
      });

      if (!signupRes.ok) {
        const errorData = await signupRes.json();
        throw new Error(errorData.detail || "Signup failed");
      }

      console.log("Account created, logging in...");
      const loginRes = await fetch("http://localhost:8000/login", {
        method: "POST",
        headers: { 
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ username, password }),
      });

      if (!loginRes.ok) {
        const errorData = await loginRes.json();
        throw new Error(errorData.detail || "Login failed");
      }

      const loginData = await loginRes.json();
      localStorage.setItem("token", loginData.token);
      onAuthSuccess();
    } catch (error) {
      console.error("Signup/Login error:", error);
      alert(error.message || "Is the backend server running? (http://localhost:8000)");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="p-4 bg-white rounded-lg shadow">
      <h2 className="text-2xl mb-4">Sign Up for MuseMate</h2>
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
        {isLoading ? "Creating Account..." : "Sign Up"}
      </button>
    </form>
  );
}