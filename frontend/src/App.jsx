import React from "react";
import ChatUI from "./components/ChatUI";
import { GoogleOAuthProvider } from "@react-oauth/google";
import { AuthProvider } from "./context/AuthContext";

const App = () => {
  return (
    <GoogleOAuthProvider clientId=ENTER YOUR CLIENT ID>
      <AuthProvider>
        <ChatUI />
      </AuthProvider>
    </GoogleOAuthProvider>
  );
};

export default App;
