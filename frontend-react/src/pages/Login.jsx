import React, { useState } from "react";
import api from "../api/axios";
import "./Login.css"; // <-- flask animation styles

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const res = await api.post("/auth/login/", { username, password });
      localStorage.setItem("token", res.data.token);
      window.location.href = "/dashboard";
    } catch (err) {
      setError("Invalid credentials");
    }
  };

  return (
    <div className="login-container">
      {/* LEFT ANIMATION PANEL */}
      <div className="left-panel">
        <h1 className="left-main-title">FOSSEE Intern Screening</h1>
        <div className="flask">
          <div className="liquid"></div>
          <div className="bubble bubble1"></div>
          <div className="bubble bubble2"></div>
          <div className="bubble bubble3"></div>
        </div>

        <h2 className="chem-title">Chemical Equipment Visualizer</h2>
      </div>

      {/* RIGHT LOGIN CARD */}
      <div className="right-panel">
        <form onSubmit={handleLogin} className="login-card">
          <h1 className="login-title">Login</h1>

          {error && <p className="error-text">{error}</p>}

          <input
            className="input-box"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />

          <input
            className="input-box"
            placeholder="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <button className="login-btn" type="submit">
            LOGIN
          </button>

          <button
            type="button"
            className="register-btn"
            onClick={() => (window.location.href = "/register")}
          >
            Create an Account
          </button>
        </form>
      </div>
    </div>
  );
}
