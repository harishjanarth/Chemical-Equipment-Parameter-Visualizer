import React from "react";
import { Drawer, List, ListItemButton, ListItemText, Toolbar, Box, Typography } from "@mui/material";
import { useNavigate } from "react-router-dom";

export default function Sidebar() {
  const navigate = useNavigate();

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: 240,
        flexShrink: 0,
        [`& .MuiDrawer-paper`]: { width: 240, boxSizing: "border-box" },
      }}
    >
      <Toolbar />
      <Box sx={{ p: 2 }}>
        <Typography variant="h6" noWrap>Visualizer</Typography>
      </Box>

      <List>
        <ListItemButton onClick={() => navigate("/dashboard")}>
          <ListItemText primary="Dashboard" />
        </ListItemButton>

        <ListItemButton onClick={() => navigate("/upload")}>
          <ListItemText primary="Upload CSV" />
        </ListItemButton>

        <ListItemButton onClick={() => navigate("/history")}>
          <ListItemText primary="History" />
        </ListItemButton>

        <ListItemButton
          sx={{ mt: 2, color: "red" }}
          onClick={() => {
            localStorage.removeItem("token");
            navigate("/");
          }}
        >
          <ListItemText primary="Logout" />
        </ListItemButton>
      </List>
    </Drawer>
  );
}
