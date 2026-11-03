# D3.js v7 Cheat Sheet

Official docs: https://d3js.org/ — API index: https://d3js.org/api — Examples: https://observablehq.com/@d3/gallery

> Tip: in VS Code, press `Ctrl+Shift+V` to view this file rendered.
> A complete working example of everything in section 10–11 is in [linked_views.html](linked_views.html).

---

## 1. Setup and loading data

### Script tags (order matters: data and d3 before your code)
```html
<script src="data.js"></script>       <!-- defines: const data = [ {...}, {...} ] -->
<script src="d3.v7.min.js"></script>  <!-- or https://cdn.jsdelivr.net/npm/d3@7 -->
<script>
  console.log(data.length, data[0]);  // data is a global array of objects
</script>
```
`data.js` is the easiest option: it works when you double-click the HTML file (`file://`).

### Loading a CSV / JSON file directly
```js
d3.csv("converted_data.csv", d3.autoType).then(data => {
  // d3.autoType turns "17.99" into the number 17.99 (CSV values are strings otherwise!)
  draw(data);
});
d3.json("file.json").then(data => draw(data));
```
⚠ `d3.csv` / `d3.json` **do not work from `file://`** (the browser blocks it). Run a local server:
`python -m http.server` then open http://localhost:8000/visu.html (or use the VS Code "Live Server" extension).

Without `autoType`, convert by hand:
```js
d3.csv("file.csv", d => ({ radius: +d.radius_mean, texture: +d.texture_mean }))
```

---

## 2. Exploring and sampling data

```js
Object.keys(data[0])                    // column names
data.length                             // number of individuals (rows)

d3.min(data, d => d.radius_mean)
d3.max(data, d => d.radius_mean)
d3.extent(data, d => d.radius_mean)     // [min, max]  ← used for scale domains
d3.mean / d3.median / d3.sum / d3.deviation (data, d => d.radius_mean)
d3.quantile(data.map(d => d.area_mean).sort(d3.ascending), 0.75)

// Grouping (e.g. if you have a "diagnosis" column)
d3.group(data, d => d.diagnosis)                     // Map: "M" -> [rows], "B" -> [rows]
d3.rollup(data, v => v.length, d => d.diagnosis)     // Map: "M" -> 212, "B" -> 357
d3.rollup(data, v => d3.mean(v, d => d.area_mean), d => d.diagnosis)

// Sorting (copy first: sort() modifies the array)
data.slice().sort((a, b) => d3.descending(a.area_mean, b.area_mean))
```

### Sampling
```js
data.slice(0, 50)                               // first 50 rows
d3.shuffle(data.slice()).slice(0, 100)          // 100 random rows (random sample)
data.filter((d, i) => i % 10 === 0)             // every 10th row (systematic sample)
data.filter(d => d.radius_mean > 15)            // condition-based subset

// Give every individual a stable id (needed to link charts later!)
data.forEach((d, i) => d.id = i);
```

---

## 3. Selections: find and modify DOM elements

```js
d3.select("#container")           // first match (CSS selector)
d3.selectAll("circle")            // all matches

sel.append("p")                   // create a child, returns the new element
sel.text("hello")                 // text content
sel.attr("r", 5)                  // attribute (SVG geometry: x, y, r, width, fill...)
sel.style("color", "red")         // CSS style
sel.classed("selected", true)     // add/remove a CSS class  ← best for highlighting
sel.remove()                      // delete
sel.raise()                       // move to front (drawn on top)
sel.on("click", (event, d) => { ... })   // event; d = the bound datum
sel.filter(d => d.radius_mean > 20)
```
Every setter accepts a **function of the data**: `.attr("r", d => d.area_mean / 100)`.
Methods return the selection → you can **chain** them.

---

## 4. Data join: one element per data row

```js
d3.select("#container")
  .selectAll("p")          // "the p elements I want" (none exist yet)
  .data(data)              // bind one row to each
  .join("p")               // create missing ones, remove extra ones
  .text(d => d.texture_mean);
```
Old style (what you saw in class) is equivalent: `.data(data).enter().append("p")`.

Full control of enter / update / exit:
```js
sel.data(newData, d => d.id)       // key function: match rows by id, not by index
   .join(
     enter  => enter.append("circle").attr("r", 0),
     update => update,
     exit   => exit.remove()
   )
   .attr("cx", d => x(d.radius_mean));
```

---

## 5. SVG + margin convention (use this for every chart)

```js
const width = 500, height = 300;
const margin = { top: 20, right: 20, bottom: 40, left: 50 };
const innerW = width - margin.left - margin.right;
const innerH = height - margin.top - margin.bottom;

const svg = d3.select("#container").append("svg")
    .attr("width", width).attr("height", height);
const g = svg.append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);
// draw everything inside g, in the area [0, innerW] x [0, innerH]
```
SVG shapes: `circle (cx, cy, r)`, `rect (x, y, width, height)`, `line (x1,y1,x2,y2)`,
`path (d)`, `text (x, y)`, `g` (group, moved with `transform`).
⚠ In SVG, **y = 0 is at the top**.

---

## 6. Scales: data value → pixels / colors

```js
const x = d3.scaleLinear()
    .domain(d3.extent(data, d => d.radius_mean))  // data space
    .range([0, innerW])                           // pixel space
    .nice();                                      // round the ends

const y = d3.scaleLinear()
    .domain([0, d3.max(data, d => d.area_mean)])
    .range([innerH, 0]);                          // inverted: big values go up

x(15)          // value → pixel
x.invert(120)  // pixel → value (useful with brushes / mouse)

d3.scaleLog()                                     // skewed data (domain must be > 0)
d3.scaleSqrt()                                    // circle radius ∝ value (area)
d3.scaleBand().domain(["M","B"]).range([0, innerW]).padding(0.2)  // bar charts
   // x.bandwidth() = width of one bar
d3.scaleOrdinal().domain(["M","B"]).range(["#e4572e", "#4c78a8"]) // category → color
d3.scaleOrdinal(d3.schemeCategory10)
d3.scaleSequential(d3.interpolateViridis).domain([min, max])     // number → color
```

---

## 7. Axes

```js
g.append("g")
  .attr("transform", `translate(0,${innerH})`)   // x axis at the bottom
  .call(d3.axisBottom(x).ticks(6));
g.append("g")
  .call(d3.axisLeft(y));

// Axis labels
g.append("text").attr("x", innerW / 2).attr("y", innerH + 35)
  .attr("text-anchor", "middle").text("radius_mean");
g.append("text").attr("transform", "rotate(-90)")
  .attr("x", -innerH / 2).attr("y", -38)
  .attr("text-anchor", "middle").text("area_mean");
```
Options: `.ticks(5)`, `.tickFormat(d3.format(".1f"))`, `.tickSize(-innerW)` (grid lines).

---

## 8. Common charts

### Scatter plot
```js
g.selectAll("circle").data(data).join("circle")
  .attr("cx", d => x(d.radius_mean))
  .attr("cy", d => y(d.texture_mean))
  .attr("r", 3)
  .attr("fill", "steelblue").attr("opacity", 0.6);
```

### Histogram (d3.bin)
```js
const x = d3.scaleLinear().domain(d3.extent(data, d => d.area_mean)).nice().range([0, innerW]);

const bins = d3.bin()
    .value(d => d.area_mean)
    .domain(x.domain())
    .thresholds(x.ticks(20))(data);
// each bin is an ARRAY of the individuals in it, plus bin.x0 and bin.x1 (its bounds)

const y = d3.scaleLinear().domain([0, d3.max(bins, b => b.length)]).nice().range([innerH, 0]);

g.selectAll("rect").data(bins).join("rect")
  .attr("x", b => x(b.x0) + 1)
  .attr("width", b => Math.max(0, x(b.x1) - x(b.x0) - 1))
  .attr("y", b => y(b.length))
  .attr("height", b => innerH - y(b.length))
  .attr("fill", "steelblue");
```

### Bar chart (categories)
```js
const counts = d3.rollups(data, v => v.length, d => d.diagnosis); // [["M",212],["B",357]]
const x = d3.scaleBand().domain(counts.map(c => c[0])).range([0, innerW]).padding(0.2);
const y = d3.scaleLinear().domain([0, d3.max(counts, c => c[1])]).range([innerH, 0]);
g.selectAll("rect").data(counts).join("rect")
  .attr("x", c => x(c[0])).attr("width", x.bandwidth())
  .attr("y", c => y(c[1])).attr("height", c => innerH - y(c[1]));
```

### Line chart
```js
const line = d3.line().x(d => x(d.date)).y(d => y(d.value));
g.append("path").datum(sortedData)
  .attr("d", line).attr("fill", "none").attr("stroke", "steelblue");
```

---

## 9. Interaction basics

```js
// Hover
circles
  .on("mouseover", (event, d) => d3.select(event.currentTarget).attr("r", 6))
  .on("mouseout",  (event, d) => d3.select(event.currentTarget).attr("r", 3));

// Simplest tooltip: an SVG <title> (browser shows it on hover)
circles.append("title").text(d => `radius: ${d.radius_mean}\ntexture: ${d.texture_mean}`);

// Mouse position inside an element
const [mx, my] = d3.pointer(event, g.node());

// Animation
circles.transition().duration(500).attr("cx", d => x(d.area_mean));
```
⚠ With arrow functions `this` doesn't work — use `event.currentTarget` instead.

---

## 10. Brushing (selecting with a rectangle)

```js
const brush = d3.brush()                      // 2D; d3.brushX() for histograms (1D)
    .extent([[0, 0], [innerW, innerH]])
    .on("brush end", ({ selection }) => {
      if (!selection) return;                 // null = the user cleared the brush
      const [[x0, y0], [x1, y1]] = selection; // pixels!
      circles.classed("selected", d =>
        x0 <= x(d.radius_mean) && x(d.radius_mean) <= x1 &&
        y0 <= y(d.texture_mean) && y(d.texture_mean) <= y1);
    });

g.append("g").call(brush);

// brushX: selection is just [x0, x1]
// clear a brush from code: brushG.call(brush.move, null)
```
CSS for highlighting:
```css
circle.selected { fill: #e4572e; opacity: 1; }
```

---

## 11. Linked (synchronised) views

**Idea:** the selection is not stored in a chart, it is stored in **one shared variable**.
Any chart can change it; every chart redraws itself from it.

```js
data.forEach((d, i) => d.id = i);    // stable id per individual

let selected = new Set();            // shared state: ids of selected individuals
const views = [];                    // each chart pushes its update function here

function setSelection(ids) {
  selected = new Set(ids);
  views.forEach(update => update(selected));
}
```

**Scatter plot** reacts by coloring the selected points:
```js
views.push(sel => {
  circles.classed("selected", d => sel.has(d.id))
         .classed("dim", d => sel.size > 0 && !sel.has(d.id));
});
circles.on("click", (event, d) => setSelection([d.id]));   // select one individual
```

**Histogram** reacts by coloring the bins where selected individuals appear.
Draw two layers of bars with the same bins: grey = everyone, colored = selected ones only.
```js
const allBars = g.append("g").selectAll("rect").data(bins).join("rect")
   .attr("fill", "#ccc") /* x, width, y, height as in section 8 */;

const selBars = g.append("g").selectAll("rect").data(bins).join("rect")
   .attr("fill", "#e4572e")
   .attr("x", b => x(b.x0) + 1).attr("width", b => Math.max(0, x(b.x1) - x(b.x0) - 1))
   .attr("y", innerH).attr("height", 0);

views.push(sel => {
  const nSel = b => b.filter(d => sel.has(d.id)).length;   // selected in this bin
  selBars.attr("y", b => y(nSel(b)))
         .attr("height", b => innerH - y(nSel(b)));
  allBars.classed("has-selected", b => nSel(b) > 0);       // e.g. outline the bin
});
```

**Any brush writes to the shared state** instead of coloring directly:
```js
brush.on("brush end", ({ selection, sourceEvent }) => {
  if (!sourceEvent) return;               // ignore brush.move called from code
  if (!selection) return setSelection([]);
  const [x0, x1] = selection;             // brushX on a histogram
  setSelection(data.filter(d => x0 <= x(d.area_mean) && x(d.area_mean) <= x1).map(d => d.id));
});
```

Alternative with D3's event system (same idea):
```js
const dispatcher = d3.dispatch("select");
dispatcher.on("select.scatter", ids => { /* update scatter */ });  // ".name" is required
dispatcher.on("select.hist",    ids => { /* update histogram */ }); // for several listeners
dispatcher.call("select", null, ids);
```

---

## 12. Common pitfalls

| Symptom | Cause / fix |
|---|---|
| Blank page | Open the console (F12). `d3 is not defined` → d3 script missing or loaded after your code. |
| `d.xxx` is `undefined` | Wrong column name → `console.log(Object.keys(data[0]))`. |
| Weird sorting / scales | CSV values are strings → `d3.autoType` or `+d.value`. |
| `d3.csv` fails | You're on `file://` → use a local server or `data.js`. |
| Chart upside down | y range must be `[innerH, 0]`. |
| Nothing visible in SVG | Missing `width`/`height`, or shapes are outside the drawing area. |
| Click on points doesn't work | Brush overlay is on top → append the brush **before** the points. |
| `this` is wrong in handler | Arrow function → use `event.currentTarget`. |

---

## 13. Docs to bookmark

- Selections: https://d3js.org/d3-selection
- Data join: https://d3js.org/d3-selection/joining
- Scales: https://d3js.org/d3-scale
- Axes: https://d3js.org/d3-axis
- Arrays / stats / bin / group: https://d3js.org/d3-array
- Shapes (line, area, pie): https://d3js.org/d3-shape
- Brush: https://d3js.org/d3-brush
- Transitions: https://d3js.org/d3-transition
- Dispatch: https://d3js.org/d3-dispatch
- Fetch (csv/json): https://d3js.org/d3-fetch
