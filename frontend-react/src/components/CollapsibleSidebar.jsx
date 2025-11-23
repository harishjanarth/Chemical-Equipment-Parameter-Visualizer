import React from "react";
import { Drawer, List, ListItemButton, ListItemText, Box, Divider, Typography } from "@mui/material";
import { useNavigate } from "react-router-dom";

export default function CollapsibleSidebar({ open, onClose }) {
  const navigate = useNavigate();

  const go = (path) => {
    navigate(path);
    onClose();
  };

  return (
  <Drawer
    open={open}
    onClose={onClose}
    PaperProps={{
      sx: {
        width: 260,
        background: "linear-gradient(180deg, rgba(255,255,255,0.04), rgba(0,0,0,0.06))",
        backdropFilter: "blur(10px)",
      }
    }}
    slotProps={{
      backdrop: {
        sx: { backgroundColor: "transparent" }  // 👈 No dull background
      }
    }}
  >
    <Box sx={{ width: 260, p: 2 }}>
      <Typography variant="h6" sx={{ mb: 1, fontWeight: 800 }}>Visualizer</Typography>

      <List>
        <ListItemButton onClick={() => go("/dashboard")} sx={{ borderRadius: 1, mb: 0.5 }}>
          <ListItemText primary="Dashboard" primaryTypographyProps={{ fontWeight: 700 }} />
        </ListItemButton>

        <ListItemButton onClick={() => go("/history")} sx={{ borderRadius: 1, mb: 0.5 }}>
          <ListItemText primary="History" primaryTypographyProps={{ fontWeight: 700 }} />
        </ListItemButton>
      </List>

      <Divider sx={{ my: 1 }} />

      <List>
        <ListItemButton
          onClick={() => { localStorage.removeItem("token"); go("/"); }}
          sx={{ borderRadius: 1 }}
        >
          <ListItemText
            primary="Logout"
            primaryTypographyProps={{
              sx: { color: "error.main", fontWeight: 700 }
            }}
          />
        </ListItemButton>
      </List>
    </Box>
  </Drawer>
);
}