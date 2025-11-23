import React from "react";
import { AppBar, Toolbar, IconButton, Typography, Box, Switch } from "@mui/material";
import MenuIcon from "@mui/icons-material/Menu";
import Brightness4Icon from "@mui/icons-material/Brightness4";
import Brightness7Icon from "@mui/icons-material/Brightness7";

export default function TopBar({ onMenuToggle, mode, toggleMode }) {
  return (
    <AppBar position="sticky" color="transparent" elevation={0}
      sx={{
        backdropFilter: "blur(8px)",
        background: mode === "light" ? "rgba(255,255,255,0.75)" : "rgba(20,20,20,0.65)",
        borderBottom: mode === "light" ? "1px solid rgba(0,0,0,0.06)" : "1px solid rgba(255,255,255,0.04)",
        boxShadow: mode === "light" ? "0 4px 20px rgba(12,20,30,0.04)" : "0 4px 20px rgba(0,0,0,0.6)"
      }}>
      <Toolbar sx={{ display: "flex", alignItems: "center", gap: 2 }}>
        <IconButton onClick={onMenuToggle} edge="start" size="large" aria-label="menu">
          <MenuIcon sx={{ color: mode === "light" ? "#222" : "#fff" }} />
        </IconButton>

        {/*title*/}
        <Box sx={{ display: "flex", alignItems: "center", gap: 1, mx: "auto" }}>
          <Box sx={{
            width: 36,
            height: 36,
            borderRadius: 8,
            background: mode === "light" ? "#111" : "#ffb300",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            boxShadow: "0 6px 18px rgba(0,0,0,0.12)",
            color: "#fff",
            fontWeight: 900
          }}>
            ⌬
          </Box>

          <Typography variant="h6" sx={{ fontWeight: 900, letterSpacing: 0.2, color: mode === "light" ? "#111" : "#fff" }}>
            Chemical Equipment Parameter Visualizer
          </Typography>
        </Box>

        {/* Right controls */}
        <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          {mode === "dark" ? <Brightness4Icon sx={{ color: "#fff" }} /> : <Brightness7Icon sx={{ color: "#222" }} />}
          <Switch checked={mode === "dark"} onChange={toggleMode} />
        </Box>
      </Toolbar>
    </AppBar>
  );
}
