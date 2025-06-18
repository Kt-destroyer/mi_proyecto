import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import { MathJaxContext } from "better-react-mathjax";

const config = {
  loader: { load: ["input/asciimath", "input/tex"] }
};

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <MathJaxContext config={config}>
      <App />
    </MathJaxContext>
  </React.StrictMode>
);