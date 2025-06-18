import React from "react";
import { MathJax } from "better-react-mathjax";

const Latex: React.FC<{ children: string }> = ({ children }) => (
  <MathJax dynamic inline>{children}</MathJax>
);

export default Latex;