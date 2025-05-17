"use client";
import { useState, useEffect } from "react";
import Login from "./Login";
import Signup from "./Signup";
import Chat from "./Chat";

export default function Page() {
  const [isAuthed, setIsAuthed] = useState(false);
  const [showSignup, setShowSignup] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("token");
    setIsAuthed(!!token);
  }, []);

  function handleAuthSuccess() {
    setIsAuthed(true);
  }

  if (!isAuthed) {
    return (
      <div className="container mx-auto max-w-md p-4">
        {showSignup ? (
          <>
            <Signup onAuthSuccess={handleAuthSuccess} />
            <button 
              onClick={() => setShowSignup(false)}
              className="w-full mt-4 p-2 text-blue-500 hover:text-blue-700"
            >
              Already have an account? Log in
            </button>
          </>
        ) : (
          <>
            <Login onAuthSuccess={handleAuthSuccess} />
            <button 
              onClick={() => setShowSignup(true)}
              className="w-full mt-4 p-2 text-blue-500 hover:text-blue-700"
            >
              Need an account? Sign up
            </button>
          </>
        )}
      </div>
    );
  }

  return <Chat />;
}