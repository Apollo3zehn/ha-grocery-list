import resolve from "@rollup/plugin-node-resolve";
import typescript from "@rollup/plugin-typescript";
import terser from "@rollup/plugin-terser";

// The card is shipped as a single self-contained ES module that HA serves as a
// Lovelace resource. Lit is bundled in (HA does not provide it to custom
// cards), tree-shaken and minified so the payload stays small.
export default {
  input: "src/grocery-list-card.ts",
  output: {
    // Emit straight into the integration so HACS ships one artifact and the
    // integration can serve it as a Lovelace resource (see frontend.py).
    file: "../custom_components/grocery_list/frontend/grocery-list-card.js",
    format: "es",
    sourcemap: false,
  },
  plugins: [
    resolve(),
    typescript({ tsconfig: "./tsconfig.json" }),
    terser({ format: { comments: false } }),
  ],
};
