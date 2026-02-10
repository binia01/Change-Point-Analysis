import axios from "axios";

const API = axios.create({ baseURL: "/api" });

export const fetchPrices  = (start, end) =>
  API.get("/prices", { params: { start, end } }).then((r) => r.data);

export const fetchStats   = (start, end) =>
  API.get("/stats", { params: { start, end } }).then((r) => r.data);

export const fetchEvents  = (category) =>
  API.get("/events", { params: { category: category || undefined } }).then((r) => r.data);

export const fetchCategories = () =>
  API.get("/events/categories").then((r) => r.data);

export const fetchImpacts = (category) =>
  API.get("/events/impacts", { params: { category: category || undefined } }).then((r) => r.data);

export const fetchChangePoints = () =>
  API.get("/changepoints").then((r) => r.data);
