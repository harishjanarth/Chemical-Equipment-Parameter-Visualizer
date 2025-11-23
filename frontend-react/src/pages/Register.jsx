import React, { useState } from "react";
import api from "../api/axios";
import { useNavigate } from "react-router-dom";
import "./Login.css";

export default function Register() {
  const navigate = useNavigate();
  const [username, setUser] = useState("");
  const [password, setPass] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const submit = async (e) => {
    e.preventDefault();

    if (password !== confirm) {
      setError("Passwords do not match");
      return;
    }

    try {
      await api.post("/auth/register/", { username, password });
      setSuccess("Registration successful! Redirecting...");
      setTimeout(() => navigate("/"), 1500);
    } catch {
      setError("Username already exists");
    }
  };

  return (
    <div className="login-container">
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

      {/* RIGHT REGISTER CARD */}
      <div className="right-panel">
        <form onSubmit={submit} className="login-card">
          <h1 className="login-title">Create an Account</h1>

          {error && <p className="error-text">{error}</p>}
          {success && <p className="success-text">{success}</p>}

          <input
            className="input-box"
            placeholder="Username"
            value={username}
            onChange={(e) => setUser(e.target.value)}
          />

          <input
            className="input-box"
            placeholder="Password"
            type="password"
            value={password}
            onChange={(e) => setPass(e.target.value)}
          />

          <input
            className="input-box"
            placeholder="Confirm Password"
            type="password"
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
          />

          <button className="login-btn" type="submit">
            REGISTER
          </button>

          <button
            type="button"
            className="register-btn"
            onClick={() => navigate("/")}
          >
            Back to Login
          </button>
        </form>
      </div>
    </div>
  );
}
