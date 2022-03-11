// import fetch from "node-fetch";
// import { JSDOM } from "jsdom";
// (async () => {
//   const response = await fetch(
//     "https://cloud.google.com/bigquery/docs/reference/standard-sql/functions-and-operators"
//   );
//   const body = await response.text();
//   const dom = new JSDOM(body);
//   const doc = dom.window.document;
//   // @ts-ignore
//   const sections = Array.from(doc.querySelectorAll("h3").values());
//   const codes = sections
//     // @ts-ignore
//     .map((section) => section.nextElementSibling)
//     .filter((section) => section instanceof HTMLElement)
//     .map((section) => section.querySelector("lang-sql"));
//   console.log(codes[0]);
// })();
//let el: HTMLButtonElement = new HTMLButtonElement();

console.log("Hello");
