import React, { useEffect, useState } from "react";
import {
  Box,
  Paper,
  Typography,
  Button,
  Collapse,
  CircularProgress
} from "@mui/material";

import TopBar from "../components/TopBar";
import CollapsibleSidebar from "../components/CollapsibleSidebar";
import api from "../api/axios";

export default function History({ mode, toggleMode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [items, setItems] = useState([]);
  const [expanded, setExpanded] = useState({});
  const [tableData, setTableData] = useState({});
  const [loadingData, setLoadingData] = useState({});

  // sorting state
  const [sortConfig, setSortConfig] = useState({
    id: null,
    field: null,
    direction: "asc",
  });

  // fetch history
  const fetchHistory = async () => {
    try {
      const res = await api.get("/history/");
      setItems(res.data);
    } catch (err) {
      console.error("History load error:", err);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  // load dataset rows
  const loadDatasetData = async (id) => {
    setLoadingData((p) => ({ ...p, [id]: true }));
    try {
      const res = await api.get(`/dataset/${id}/data/`);
      setTableData((p) => ({ ...p, [id]: res.data }));
    } catch (err) {
      console.error("Dataset load error", err);
    } finally {
      setLoadingData((p) => ({ ...p, [id]: false }));
    }
  };

  // sorting function
  const sortTable = (datasetId, field) => {
    setTableData((prev) => {
      const data = prev[datasetId];
      if (!data) return prev;

      let direction = "asc";
      if (sortConfig.field === field && sortConfig.direction === "asc") {
        direction = "desc";
      }

      const sortedRows = [...data.rows].sort((a, b) => {
        const av = Number(a[field]);
        const bv = Number(b[field]);
        return direction === "asc" ? av - bv : bv - av;
      });

      return {
        ...prev,
        [datasetId]: {
          ...data,
          rows: sortedRows,
        },
      };
    });

    setSortConfig({
      id: datasetId,
      field,
      direction: sortConfig.field === field && sortConfig.direction === "asc"
        ? "desc"
        : "asc",
    });
  };

  // colors
  const COLORS = ["#26a69a", "#42a5f5", "#ef5350", "#ab47bc", "#ffa726", "#8d6e63"];

  const renderDistBar = (dist) => {
    if (!dist) return null;
    const total = Object.values(dist).reduce((a, b) => a + b, 0);

    return (
      <Box sx={{ display: "flex", height: 32, overflow: "hidden", borderRadius: 2, mb: 2 }}>
        {Object.entries(dist).map(([type, count], i) => (
          <Box
            key={type}
            sx={{
              width: `${(count / total) * 100}%`,
              background: COLORS[i % COLORS.length],
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              color: "white",
              fontWeight: 700,
              fontSize: "0.75rem",
            }}
          >
            {type} — {count}
          </Box>
        ))}
      </Box>
    );
  };

  return (
    <Box sx={{ minHeight: "100vh", bgcolor: mode === "light" ? "#f5f5f5" : "#0b0b0b" }}>
      <TopBar onMenuToggle={() => setSidebarOpen(true)} mode={mode} toggleMode={toggleMode} />
      <CollapsibleSidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <Box sx={{ p: 4, maxWidth: "1100px", mx: "auto" }}>
        <Typography
          variant="h4"
          sx={{ fontWeight: 800, textAlign: "center", mb: 4, color: "text.primary" }}
        >
          Upload History (Last 5)
        </Typography>

        {/* Show message if empty */}
        {items.length === 0 && (
          <Typography sx={{ textAlign: "center", opacity: 0.7 }}>
            No uploaded datasets yet.
          </Typography>
        )}

        {items.map((item, idx) => {
          const summary = item.summary || {};

          return (
            <Paper
              key={item.id}
              sx={{
                p: 3,
                mb: 4,
                borderRadius: 4,
                backdropFilter: "blur(12px)",
              }}
            >
              <Typography variant="h6" sx={{ fontWeight: 700 }}>
                {item.filename}
              </Typography>

              <Typography sx={{ opacity: 0.7, mb: 2 }}>{item.uploaded}</Typography>

              <Typography sx={{ fontSize: "1.05rem", mb: 1 }}>
                <b>Total:</b> {summary.total_equipment} &nbsp; | &nbsp;
                <b>Avg Flow:</b> {summary.avg_flowrate?.toFixed(2)} &nbsp; | &nbsp;
                <b>Avg Pressure:</b> {summary.avg_pressure?.toFixed(2)} &nbsp; | &nbsp;
                <b>Avg Temp:</b> {summary.avg_temperature?.toFixed(2)}
              </Typography>

              {renderDistBar(summary.type_distribution)}

              <Button
                sx={{
                  mt: 1,
                  textTransform: "none",
                  color: "#ffb300",
                  fontWeight: 700,
                }}
                onClick={() => {
                  const now = !expanded[item.id];
                  setExpanded((p) => ({ ...p, [item.id]: now }));
                  if (now && !tableData[item.id]) loadDatasetData(item.id);
                }}
              >
                {expanded[item.id] ? "Hide original data" : "View original data"}
              </Button>

              {/* collapsible table */}
              <Collapse in={expanded[item.id]}>
                <Box sx={{ mt: 2 }}>
                  {loadingData[item.id] ? (
                    <CircularProgress size={28} />
                  ) : tableData[item.id] ? (
                    <Paper sx={{ p: 2, overflowX: "auto" }}>
                      <table style={{ width: "100%", borderCollapse: "collapse" }}>
                        <thead>
                          <tr>
                            {tableData[item.id].columns.map((col) => {
                              const sortable = ["Flowrate", "Pressure", "Temperature"].includes(col);

                              const arrow =
                                sortConfig.id === item.id && sortConfig.field === col
                                  ? sortConfig.direction === "asc"
                                    ? " ▲"
                                    : " ▼"
                                  : " ▼";

                              return (
                                <th
                                  key={col}
                                  style={{
                                    padding: "8px",
                                    borderBottom: "1px solid #ccccccff",
                                    textAlign: "left",
                                    fontWeight: 700,
                                    cursor: sortable ? "pointer" : "default",
                                    userSelect: "none",
                                  }}
                                  onClick={() => sortable && sortTable(item.id, col)}
                                >
                                  {col} {sortable && <span>{arrow}</span>}
                                </th>
                              );
                            })}
                          </tr>
                        </thead>

                        <tbody>
                          {tableData[item.id].rows.map((row, rIdx) => (
                            <tr key={rIdx}>
                              {tableData[item.id].columns.map((col) => (
                                <td
                                  key={col}
                                  style={{
                                    padding: "6px 8px",
                                    borderBottom: "1px solid #eee",
                                  }}
                                >
                                  {row[col]}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </Paper>
                  ) : (
                    <Typography>No preview available.</Typography>
                  )}
                </Box>
              </Collapse>
            </Paper>
          );
        })}
      </Box>
    </Box>
  );
}
