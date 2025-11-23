import React, { useState } from "react";
import { Paper, Button, Typography } from "@mui/material";
import DashboardLayout from "../components/DashboardLayout";
import api from "../api/axios";
import { useNavigate } from "react-router-dom";

export default function Upload() {
  const [file, setFile] = useState(null);
  const navigate = useNavigate();

  const upload = async () => {
    const fd = new FormData();
    fd.append("file", file);

    try {
      const res = await api.post("/upload/", fd, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      navigate("/dashboard");

    } catch (err) {
      console.error("Upload error:", err);
    }
  };

  return (
    <DashboardLayout>
      <Typography variant="h4" gutterBottom>Upload CSV</Typography>

      <Paper sx={{ p: 5, mb: 3 }}>
        <input
          type="file"
          onChange={(e) => setFile(e.target.files[0])}
        />
      </Paper>

      <Button variant="contained" onClick={upload} disabled={!file}>
        Upload & Analyze
      </Button>
    </DashboardLayout>
  );
}
