import React, { useEffect, useState } from "react";
import {
  Box,
  Grid,
  Paper,
  Typography,
  Button,
  CircularProgress,
  Alert,
} from "@mui/material";

import UploadIcon from "@mui/icons-material/Upload";
import CloseIcon from "@mui/icons-material/Close";

import TopBar from "../components/TopBar";
import CollapsibleSidebar from "../components/CollapsibleSidebar";
import api from "../api/axios";

import TypePieChart from "../charts/TypePieChart";
import CorrelationHeatmap from "../charts/CorrelationHeatmap";

export default function DashboardAnalyze({ mode, toggleMode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [file, setFile] = useState(null);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState(null);

  const loadSummary = async () => {
    try {
      const res = await api.get("/summary/");
      setSummary(res.data);
    } catch (_) {
      setSummary(null);
    }
  };

  const loadHistory = async () => {
    try {
      const res = await api.get("/history/");
      setHistory(res.data || []);
    } catch (_) {
      setHistory([]);
    }
  };

  useEffect(() => {
    loadSummary();
    loadHistory();
  }, []);

  

  const upload = async () => {
    setError(null);

    if (!file) return setError("Please choose a CSV file first.");

    if (!file.name.toLowerCase().endsWith(".csv"))
      return setError("Invalid file type — only CSV files allowed.");

    const fd = new FormData();
    fd.append("file", file);

    setLoading(true);
    try {
      await api.post("/upload/", fd, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      await loadSummary();
      await loadHistory();
      document.getElementById("stats")?.scrollIntoView({ behavior: "smooth" });
    } catch (err) {
      setError("Upload failed. Ensure the file is valid.");
    } finally {
      setLoading(false);
    }
  };

  const clearFile = () => {
    setFile(null);
    const input = document.getElementById("upload-input");
    if (input) input.value = "";
  };

  

  const StatCard = ({ title, value }) => (
    <Paper
      sx={{
        p: 3,
        textAlign: "center",
        background: mode === "dark" ? "#181818" : "#ffffff",
        border: mode === "dark" ? "1px solid #333" : "1px solid #ddd",
        borderRadius: 3,
      }}
    >
      <Typography
        variant="subtitle2"
        sx={{ color: "text.secondary", fontWeight: 600 }}
      >
        {title}
      </Typography>

      <Typography
        variant="h4"
        sx={{
          color: "text.primary",
          fontWeight: 600,
          mt: 1,
        }}
      >
        {value}
      </Typography>
    </Paper>
  );

  

  return (
    <Box sx={{ minHeight: "100vh", bgcolor: mode === "light" ? "#f6f6f7" : "#0b0b0b" }}>
      <TopBar
        onMenuToggle={() => setSidebarOpen(true)}
        mode={mode}
        toggleMode={toggleMode}
      />

      <CollapsibleSidebar
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      <Box sx={{ p: 3, maxWidth: 1200, mx: "auto" }}>
        
        {/* ERROR */}
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {/* UPLOAD BOX */}

        <Paper
          id="upload"
          sx={{
            p: 4,
            borderRadius: 4,
            textAlign: "center",
            background: mode === "dark" ? "#111" : "#fff",
          }}
        >
          <Typography variant="h5" sx={{ mb: 3, fontWeight: 700 }}>
            Upload CSV
          </Typography>

          <Box
            sx={{
              display: "flex",
              justifyContent: "center",
              gap: 3,
              alignItems: "center",
              flexWrap: "wrap",
            }}
          >

            {/* Choose File Button */}
            <label
              htmlFor="upload-input"
              style={{ cursor: "pointer" }}
            >
              <Box
                sx={{
                  px: 3,
                  py: 1.8,
                  borderRadius: 2,
                  background: "#ffb300",
                  color: "black",
                  fontWeight: 700,
                  display: "flex",
                  alignItems: "center",
                  gap: 1,
                  boxShadow: "0 0 15px rgba(255,181,0,0.35)",
                }}
              >
                <UploadIcon />
                CHOOSE FILE
              </Box>
            </label>

            <input
              id="upload-input"
              type="file"
              accept=".csv"
              style={{ display: "none" }}
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            />

            <Typography sx={{ opacity: 0.7 }}>
              {file ? file.name : "No file chosen"}
            </Typography>

            <Button
              variant="contained"
              disabled={!file || loading}
              onClick={upload}
              sx={{
                background: "#d3d3d3",
                color: "#555",
                px: 3,
                py: 1.4,
                fontWeight: 700,
                borderRadius: 2,
              }}
            >
              {loading ? (
                <CircularProgress size={18} color="inherit" />
              ) : (
                "UPLOAD & ANALYZE"
              )}
            </Button>

            <Button
              onClick={clearFile}
              sx={{
                borderRadius: "50%",
                width: 42,
                height: 42,
                minWidth: 42,
                border: "2px solid #ffb300",
                color: "#ffb300",
              }}
            >
              <CloseIcon />
            </Button>
          </Box>
        </Paper>

        {/*STAT*/}

        <Paper
          id="stats"
          sx={{
            mt: 4,
            p: 4,
            borderRadius: 4,
            background: mode === "dark" ? "#111" : "#fff",
          }}
        >
          <Typography variant="h5" textAlign="center" fontWeight={700} mb={3}>
            Statistics
          </Typography>

          {!summary ? (
            <Typography align="center" sx={{ opacity: 0.7 }}>
              Upload a CSV to view statistics
            </Typography>
          ) : (
            <>
              <Grid container spacing={3} justifyContent="center">
                <Grid item xs={12} sm={3}>
                  <StatCard
                    title="Total Equipment"
                    value={summary.total_equipment}
                  />
                </Grid>

                <Grid item xs={12} sm={3}>
                  <StatCard
                    title="Avg Flowrate"
                    value={Number(summary.avg_flowrate).toFixed(2)}
                  />
                </Grid>

                <Grid item xs={12} sm={3}>
                  <StatCard
                    title="Avg Pressure"
                    value={Number(summary.avg_pressure).toFixed(2)}
                  />
                </Grid>

                <Grid item xs={12} sm={3}>
                  <StatCard
                    title="Avg Temperature"
                    value={Number(summary.avg_temperature).toFixed(2)}
                  />
                </Grid>
              </Grid>

              {/* Pie Chart */}
              <Box mt={4} display="flex" justifyContent="center">
                <Paper sx={{ p: 2, width: 700 }}>
                  <Typography variant="h6" textAlign="center" mb={2}>
                    Equipment Type Distribution
                  </Typography>
                  <TypePieChart data={summary.type_distribution} />
                </Paper>
              </Box>
            </>
          )}
        </Paper>

        {/* CORRELATION HEATMAP  */}

        {summary?.correlation && (
          <Paper sx={{ p: 4, mt: 4, borderRadius: 4 }}>
            <Typography variant="h6" textAlign="center" mb={2}>
              Correlation Heatmap
            </Typography>

            <Box display="flex" justifyContent="center">
              <CorrelationHeatmap data={summary.correlation} mode={mode} />
            </Box>
          </Paper>
        )}

        {/*OUTLIERS  */}

        {summary?.outliers && (
          <Paper sx={{ p: 4, mt: 4, borderRadius: 4 }}>
            <Typography variant="h6" textAlign="center" mb={2}>
              Outlier Detection
            </Typography>

            {summary.outliers.length === 0 ? (
              <Typography textAlign="center" opacity={0.6}>
                No outliers detected
              </Typography>
            ) : (
              summary.outliers.map((o, i) => (
                <Paper key={i} sx={{ p: 2, my: 1, background: "#fafafa" }}>
                  <Typography><b>Equipment:</b> {o.EquipmentName}</Typography>
                  <Typography>Flowrate: {o.Flowrate}</Typography>
                  <Typography>Pressure: {o.Pressure}</Typography>
                  <Typography>Temperature: {o.Temperature}</Typography>
                </Paper>
              ))
            )}
          </Paper>
        )}

        {/*AVERAGES */}

        {summary?.typewise_averages && (
          <Paper sx={{ p: 4, mt: 4, borderRadius: 4 }}>
            <Typography variant="h6" textAlign="center" mb={2}>
              Type-wise Averages
            </Typography>

            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr>
                  <th style={{ padding: 8, textAlign: "left" }}>Type</th>
                  <th style={{ padding: 8, textAlign: "left" }}>Avg Flowrate</th>
                  <th style={{ padding: 8, textAlign: "left" }}>Avg Pressure</th>
                  <th style={{ padding: 8, textAlign: "left" }}>
                    Avg Temperature
                  </th>
                </tr>
              </thead>

              <tbody>
                {Object.entries(summary.typewise_averages).map(([type, values]) => (
                  <tr key={type}>
                    <td style={{ padding: 8, fontWeight: 600 }}>{type}</td>
                    <td style={{ padding: 8 }}>{values.Flowrate}</td>
                    <td style={{ padding: 8 }}>{values.Pressure}</td>
                    <td style={{ padding: 8 }}>{values.Temperature}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Paper>
        )}
      </Box>
    </Box>
  );
}
