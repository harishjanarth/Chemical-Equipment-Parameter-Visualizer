import React, { useEffect, useState } from "react";
import { Typography, Paper, Grid, Box, Button } from "@mui/material";
import DashboardLayout from "../components/DashboardLayout";
import api from "../api/axios";
import TypePieChart from "../charts/TypePieChart";

export default function Summary() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  
  useEffect(() => {
    api
      .get("/summary/")
      .then((res) => {
        setData(res.data);
        setLoading(false);
      })
      .catch((e) => {
        console.error("Summary load error:", e);
        setLoading(false);
      });
  }, []);

 
  const downloadPDF = async () => {
    try {
      //fetching history to get latest dataset id
      const hist = await api.get("/history/");
      if (!hist.data.length) {
        alert("No datasets available.");
        return;
      }

      const latest = hist.data[0];
      const id = latest.id;

      const res = await api.get(`/generate_pdf/${id}/`, {
        responseType: "blob",
      });

      const url = window.URL.createObjectURL(
        new Blob([res.data], { type: "application/pdf" })
      );

      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", "Equipment_Report.pdf");
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (e) {
      console.error("PDF Download Error:", e);
    }
  };

  
  if (loading) {
    return (
      <DashboardLayout>
        <Typography variant="h5">Loading Dashboard...</Typography>
      </DashboardLayout>
    );
  }

  // No data
  if (!data) {
    return (
      <DashboardLayout>
        <Typography variant="h5">
          No summary available. Upload a CSV first.
        </Typography>
      </DashboardLayout>
    );
  }

  
  return (
    <DashboardLayout>
      {/*Title and download opt */}
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          mb: 3,
        }}
      >
        <Typography variant="h4">Dashboard</Typography>

        <Button variant="contained" color="primary" onClick={downloadPDF}>
          Download PDF Report
        </Button>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3}>
        <Grid item xs={12} sm={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6">Total Equipment</Typography>
            <Typography variant="h3">{data.total_equipment}</Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} sm={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6">Average Flowrate</Typography>
            <Typography variant="h3">
              {data.avg_flowrate.toFixed(2)}
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} sm={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6">Average Pressure</Typography>
            <Typography variant="h3">
              {data.avg_pressure.toFixed(2)}
            </Typography>
          </Paper>
        </Grid>
      </Grid>

      {/*Pie Chart*/}
      <Box sx={{ mt: 5, width: 450 }}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" align="center" gutterBottom>
            Equipment Type Distribution
          </Typography>

          <Box sx={{ height: 300 }}>
            <TypePieChart data={data.type_distribution} />
          </Box>
        </Paper>
      </Box>
    </DashboardLayout>
  );
}
