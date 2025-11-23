import React from "react";
import {
  Chart as ChartJS,
  Tooltip,
  LinearScale,
  CategoryScale,
  Title
} from "chart.js";
import { MatrixController, MatrixElement } from "chartjs-chart-matrix";
import { Chart } from "react-chartjs-2";
import ChartDataLabels from "chartjs-plugin-datalabels";


ChartJS.register(MatrixController, MatrixElement, LinearScale, CategoryScale, Tooltip, Title, ChartDataLabels);

export default function CorrelationHeatmap({ data, mode = "light" }) {
  const metrics = ["Flowrate", "Pressure", "Temperature"];

  const baseYellow = mode === "light" ? "rgba(255, 193, 7," : "rgba(255, 179, 0,";
  const baseDark = mode === "light" ? "rgba(40,40,40," : "rgba(200,200,200,";

  const centerTextColor = mode === "light" ? "#111" : "#eee";

  const chartData = {
    datasets: [
      {
        label: "Correlation Matrix",
        data: metrics.flatMap((row) =>
          metrics.map((col) => ({
            x: col,
            y: row,
            v: Number(data[row][col] ?? 0)
          }))
        ),
        width: ({ chart }) =>
          (chart.chartArea || {}).width / metrics.length - 6,
        height: ({ chart }) =>
          (chart.chartArea || {}).height / metrics.length - 6,

       
        backgroundColor: (ctx) => {
          const v = ctx.raw.v;
          const strength = Math.abs(v); 

          
          return v >= 0
            ? `${baseYellow} ${0.3 + strength * 0.7})`
            : `${baseDark} ${0.25 + strength * 0.6})`;
        },

        borderColor: mode === "light" ? "rgba(0,0,0,0.4)" : "rgba(255,255,255,0.4)",
        borderWidth: 1,

       
        datalabels: {
          display: true,
          color: centerTextColor,
          font: { weight: "bold", size: 14 },
          formatter: (val) => val.v.toFixed(2),
        }
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: (context) => `Correlation: ${context.raw.v.toFixed(3)}`
        }
      },
      title: {
        display: false
      },
      
      datalabels: {}
    },
    scales: {
      x: {
        type: "category",
        labels: metrics,
        offset: true,
        ticks: {
          font: { size: 14, weight: "600" },
          color: centerTextColor
        },
        grid: { display: false },
      },
      y: {
        type: "category",
        labels: metrics,
        offset: true,
        ticks: {
          font: { size: 14, weight: "600" },
          color: centerTextColor
        },
        grid: { display: false },
      },
    },
  };

  return (
    <div style={{ width: "100%", display: "flex", justifyContent: "center" }}>
      <div style={{ width: 420, height: 420 }}>
        <Chart type="matrix" data={chartData} options={options} />
      </div>
    </div>
  );
}
