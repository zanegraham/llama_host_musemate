"use client";
import { useState } from "react";

export default function Chat() {
  const [userInput, setUserInput] = useState("");
  const [chatLog, setChatLog] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  async function sendMessage() {
    if (!userInput.trim()) return;

    const token = localStorage.getItem("token");
    if (!token) {
      localStorage.removeItem("token");
      window.location.reload();
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ content: userInput })
      });

      if (response.status === 401) {
        localStorage.removeItem("token");
        window.location.reload();
        return;
      }

      const data = await response.json();
      setChatLog((prev) => [...prev, 
        { role: "user", content: userInput },
        { role: "assistant", content: data.reply }
      ]);
      setUserInput("");
    } catch (error) {
      console.error("Chat error:", error);
      alert("Error sending message");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="p-4">
      <h1 className="text-2xl mb-4">MuseMate Chat</h1>
      <div className="max-h-[500px] overflow-y-auto mb-4">
        {chatLog.map((msg, i) => (
          <div key={i} className={`mb-2 ${msg.role === "user" ? "font-bold" : ""}`}>
            {msg.role === "user" ? "You" : "MuseMate"}: {msg.content}
          </div>
        ))}
      </div>
      <div className="flex gap-2">
        <input
          type="text"
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !isLoading && sendMessage()}
          placeholder="Type your message..."
          disabled={isLoading}
          className="flex-1 p-2 border rounded"
        />
        <button
          onClick={sendMessage}
          disabled={isLoading}
          className="px-4 py-2 bg-blue-500 text-white rounded disabled:opacity-50"
        >
          {isLoading ? "Sending..." : "Send"}
        </button>
      </div>
    </div>
  );
}