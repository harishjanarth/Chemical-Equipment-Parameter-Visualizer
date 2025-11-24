import React, { useMemo, useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ThemeProvider, createTheme } from "@mui/material/styles";

import DashboardAnalyze from "./pages/DashboardAnalyze";
import History from "./pages/History";
import Login from "./pages/Login";
import Register from "./pages/Register";

export default function App() {
  const [mode, setMode] = useState(
    localStorage.getItem("theme") || "light"
  );

  const theme = useMemo(
    () =>
      createTheme({
        palette: {
          mode,
          primary: { main: "#ffb300" },
          background: {
            default: mode === "dark" ? "#0b0b0b" : "#f6f6f7",
            paper: mode === "dark" ? "#111111" : "#ffffff",
          },
          text: {
            primary: mode === "dark" ? "#ffffff" : "#000000",
            secondary: mode === "dark" ? "#bbbbbb" : "#444444",
          },
        },

        components: {
          MuiPaper: {
            styleOverrides: {
              root: {
                borderRadius: 12,
                backgroundImage: "none",
                transition: "0.2s ease",
              },
            },
          },
        },
      }),
    [mode]
  );

  const toggleMode = () => {
    const next = mode === "light" ? "dark" : "light";
    setMode(next);
    localStorage.setItem("theme", next);
  };

  return (
    <ThemeProvider theme={theme}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/dashboard"
            element={<DashboardAnalyze mode={mode} toggleMode={toggleMode} />}
          />
          <Route
            path="/history"
            element={<History mode={mode} toggleMode={toggleMode} />}
          />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}
