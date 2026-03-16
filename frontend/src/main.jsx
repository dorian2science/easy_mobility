import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";

// Sentry (optional — only initialises if DSN is set)
const sentryDsn = import.meta.env.VITE_SENTRY_DSN;
if (sentryDsn) {
  import("@sentry/react").then((Sentry) => {
    Sentry.init({ dsn: sentryDsn, tracesSampleRate: 0.1 });
  });
}

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
