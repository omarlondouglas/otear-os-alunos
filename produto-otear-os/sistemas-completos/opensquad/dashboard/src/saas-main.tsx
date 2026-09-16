/**
 * SaaS entry point for the dashboard.
 * Connects to ws-gateway with tenant ID from URL params.
 */
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { App } from "./App";
import "./index.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
