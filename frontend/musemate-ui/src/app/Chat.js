"use client";

import { useState } from "react";

export default function Chat() {
  const [userInput, setUserInput] = useState("");
  const [chatLog, setChatLog] = useState([]);

  async function sendMessage() {
    if (!userInput.trim()) return;

    setChatLog([...chatLog, { role: "user", content: userInput }]);

    const response = await fetch("http://localhost:8000/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ content: userInput }),
    });

    const data = await response.json();

    setChatLog((prev) => [...prev, { role: "assistant", content: data.reply }]);

    setUserInput("");
  }

  return (
    <div>
      <h1>MuseMate Chat</h1>
      <div style={{ maxHeight: "300px", overflowY: "auto" }}>
        {chatLog.map((msg, i) => (
          <p key={i} style={{ fontWeight: msg.role === "user" ? "bold" : "normal" }}>
            {msg.role === "user" ? "You" : "MuseMate"}: {msg.content}
          </p>
        ))}
      </div>
      <input
        type="text"
        value={userInput}
        onChange={(e) => setUserInput(e.target.value)}
        placeholder="Type your message..."
      />
      <button onClick={sendMessage}>Send</button>
    </div>
  );
}
