import React from "react";
import { Pie } from "react-chartjs-2";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";
ChartJS.register(ArcElement, Tooltip, Legend);

export default function TypePieChart({ data }) {
  const labels = Object.keys(data || {});
  const values = Object.values(data || {});

  const palette = ["#ffb300", "#2b6cb0", "#66bb6a", "#f97316", "#7c3aed", "#ef5350", "#4dabf5"];

  return (
    <div style={{ height: 300 }}>
      <Pie
        data={{
          labels,
          datasets: [{ data: values, backgroundColor: labels.map((_, i) => palette[i % palette.length]) }],
        }}
        options={{ maintainAspectRatio: false, plugins: { legend: { position: "bottom" } } }}
      />
    </div>
  );
}
