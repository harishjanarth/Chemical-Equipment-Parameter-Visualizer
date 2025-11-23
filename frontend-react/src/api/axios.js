import axios from "axios";

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL + "/api/", 
  withCredentials: false,
});

api.interceptors.request.use(cfg => {
  const token = localStorage.getItem("token"); // fixed typo
  if (token) cfg.headers.Authorization = `Bearer ${token}`;
  return cfg;
});

export default api;
