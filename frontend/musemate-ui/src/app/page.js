"use client";

import { useState, useEffect } from "react";
import Chat from "./Chat";
import Login from "./Login";
import Signup from "./Signup";

export default function Page() {
  const [isAuthed, setIsAuthed] = useState(false);

  // Only run this on the client side after mount
  useEffect(() => {
    setIsAuthed(!!localStorage.getItem("token"));
  }, []);

  return (
    <main>
      <h1>MuseMate</h1>
      {isAuthed ? (
        <Chat />
      ) : (
        <>
          <Login onAuthSuccess={() => setIsAuthed(true)} />
          <Signup />
        </>
      )}
    </main>
  );
}
