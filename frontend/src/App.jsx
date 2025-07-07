import React from "react";
import ChatUI from "./components/ChatUI";
import { GoogleOAuthProvider } from "@react-oauth/google";
import { AuthProvider } from "./context/AuthContext";

const App = () => {
  return (
    <GoogleOAuthProvider clientId="419802293815-q2fip29gsq6pp4d2e20itms3dualjbnu.apps.googleusercontent.com">
      <AuthProvider>
        <ChatUI />
      </AuthProvider>
    </GoogleOAuthProvider>
  );
};

export default App;
