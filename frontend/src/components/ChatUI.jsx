import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import { prism } from "react-syntax-highlighter/dist/esm/styles/prism";
import { useAuth } from "../context/AuthContext";
import { GoogleLogin } from "@react-oauth/google";
import { jwtDecode } from "jwt-decode";

const ChatUI = () => {
  const [question, setQuestion] = useState("");
  const [chat, setChat] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const chatEndRef = useRef(null);
  const { user, login, logout } = useAuth();

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chat, loading]);

  useEffect(() => {
    const observer = new MutationObserver(() => {
      setIsDarkMode(document.documentElement.classList.contains("dark"));
    });
    observer.observe(document.documentElement, { attributes: true });
    return () => observer.disconnect();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim() || !user) return;

    const userMsg = { role: "user", content: question };
    setChat((prev) => [...prev, userMsg]);
    setQuestion("");
    setLoading(true);

    try {
      const response = await axios.post("http://localhost:8000/ask", {
        question,
      });

      const botMsg = { role: "bot", content: response.data.answer };
      setChat((prev) => [...prev, botMsg]);
    } catch (error) {
      const errorMsg = {
        role: "bot",
        content: "❌ Error: Could not fetch answer.",
      };
      setChat((prev) => [...prev, errorMsg]);
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const toggleTheme = () => {
    document.documentElement.classList.toggle("dark");
  };

  const components = {
    code({ inline, className, children, ...props }) {
      const match = /language-(\w+)/.exec(className || "");
      if (inline) {
        return (
          <code className="bg-gray-200 dark:bg-gray-700 px-1 rounded">
            {children}
          </code>
        );
      }
      return (
        <SyntaxHighlighter
          style={isDarkMode ? oneDark : prism}
          language={match?.[1] || "python"}
          PreTag="div"
          wrapLongLines
          {...props}
        >
          {String(children).replace(/\n$/, "")}
        </SyntaxHighlighter>
      );
    },
  };

  return (
    <div className="min-h-screen bg-white dark:bg-gray-900 text-gray-800 dark:text-gray-100">
      <div className="max-w-2xl mx-auto py-10 px-4">
        {/* Top Bar */}
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold">💬 Pydantic AI Chatbot</h1>
          <div className="flex gap-3">
            <button
              onClick={toggleTheme}
              className="px-3 py-1 text-sm rounded bg-gray-200 dark:bg-gray-700 dark:text-gray-100 hover:bg-gray-300 dark:hover:bg-gray-600"
            >
              🌓 Toggle Theme
            </button>
            {user && (
              <button
                onClick={logout}
                className="px-3 py-1 text-sm rounded bg-red-600 text-white hover:bg-red-700"
              >
                🚪 Logout
              </button>
            )}
          </div>
        </div>

        {/* Chat History */}
        <div className="bg-gray-100 dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-md p-4 h-[500px] overflow-y-auto space-y-4">
          {chat.map((msg, idx) => (
            <div
              key={idx}
              className={`p-3 rounded-md max-w-[85%] whitespace-pre-wrap ${
                msg.role === "user"
                  ? "bg-blue-100 dark:bg-blue-900 self-end ml-auto"
                  : "bg-gray-200 dark:bg-gray-700 self-start"
              }`}
            >
              <div className="text-sm font-medium mb-1">
                {msg.role === "user" ? "🧑 You" : "🤖 Bot"}
              </div>
              <div className="prose prose-sm dark:prose-invert max-w-none">
                <ReactMarkdown components={components}>
                  {msg.content}
                </ReactMarkdown>
              </div>
            </div>
          ))}

          {loading && (
            <div className="bg-gray-200 dark:bg-gray-700 p-3 rounded-md max-w-[85%] self-start">
              <div className="text-sm font-medium mb-1">🤖 Bot</div>
              <div className="text-sm text-gray-500 italic animate-pulse">Typing...</div>
            </div>
          )}

          <div ref={chatEndRef} />
        </div>

        {/* Chat Input or Login */}
        <div className="mt-4">
          {user ? (
            <form onSubmit={handleSubmit} className="flex gap-2">
              <textarea
                className="w-full p-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-100 rounded-md resize-none"
                rows="2"
                placeholder="Ask your question..."
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
              ></textarea>
              <button
                type="submit"
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
                disabled={loading}
              >
                Send
              </button>
            </form>
          ) : (
            <div className="flex flex-col items-center space-y-4">
              <p className="text-gray-500 dark:text-gray-300 text-sm">
                🔒 Please log in to start chatting.
              </p>
              <GoogleLogin
                onSuccess={(credentialResponse) => {
                  const decoded = jwtDecode(credentialResponse.credential);
                  login(decoded);
                }}
                onError={() => {
                  console.error("Login Failed");
                }}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChatUI;
