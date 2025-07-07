import React from "react";
import ChatUI from "./components/ChatUI";
import { GoogleOAuthProvider } from "@react-oauth/google";
import { AuthProvider } from "./context/AuthContext";

const App = () => {
  return (
    <GoogleOAuthProvider clientId={import.meta.env.VITE_GOOGLE_CLIENT_ID}>
      <AuthProvider>
        <ChatUI />
      </AuthProvider>
    </GoogleOAuthProvider>
  );
};

export default App;
