// Hover and arrow-key readout for the inline token charts (`svg.tok-chart` in agents.md).

const SVG_NS = "http://www.w3.org/2000/svg";
const fmt = (n) => Number(n).toLocaleString("en-US");

function attach(svg) {
  const dots = [...svg.querySelectorAll("circle[data-call]")];
  const calls = [...new Set(dots.map((d) => Number(d.dataset.call)))];
  const xOf = (call) => Number(dots.find((d) => Number(d.dataset.call) === call).getAttribute("cx"));

  const wrap = document.createElement("div");
  wrap.className = "tok-wrap";
  svg.replaceWith(wrap);
  wrap.append(svg);
  const tip = document.createElement("div");
  tip.className = "tok-tip";
  tip.hidden = true;
  wrap.append(tip);
  const guide = document.createElementNS(SVG_NS, "line");
  guide.setAttribute("class", "tok-guide");
  guide.setAttribute("y1", svg.dataset.top);
  guide.setAttribute("y2", svg.dataset.bottom);
  guide.style.display = "none";
  svg.querySelector(".tok-line").before(guide);

  let current = null;
  const show = (call) => {
    current = call;
    const x = xOf(call);
    guide.setAttribute("x1", x);
    guide.setAttribute("x2", x);
    guide.style.display = "";
    const here = dots.filter((d) => Number(d.dataset.call) === call);
    dots.forEach((d) => d.classList.toggle("tok-active", here.includes(d)));
    // eager's total so far, or its final total once it has stopped calling
    const eager = Math.max(
      ...dots.filter((d) => d.dataset.mode === "eager" && Number(d.dataset.call) <= call).map((d) => Number(d.dataset.total)),
    );
    const row = (mode, total, note) =>
      `<div><span class="tok-swatch tok-${mode}"></span>${mode}: ${fmt(total)}` +
      (note ? ` <span class="tok-muted">(${note})</span>` : "") + "</div>";
    const deferred = here.find((d) => d.dataset.mode === "deferred");
    tip.innerHTML =
      `<strong>after call ${call}</strong>` +
      row("eager", eager, here.some((d) => d.dataset.mode === "eager") ? "" : "done") +
      (deferred ? row("deferred", deferred.dataset.total, `${Math.round((deferred.dataset.total / eager - 1) * 100)}%`.replace("-", "\u2212")) : "");
    tip.hidden = false;
    const scale = svg.clientWidth / svg.viewBox.baseVal.width;
    const left = x * scale;
    const flip = left > svg.clientWidth / 2;
    tip.style.left = flip ? "" : `${left + 12}px`;
    tip.style.right = flip ? `${svg.clientWidth - left + 12}px` : "";
  };
  const hide = () => {
    current = null;
    guide.style.display = "none";
    dots.forEach((d) => d.classList.remove("tok-active"));
    tip.hidden = true;
  };

  svg.addEventListener("pointermove", (ev) => {
    const pt = new DOMPoint(ev.clientX, ev.clientY).matrixTransform(svg.getScreenCTM().inverse());
    show(calls.reduce((a, b) => (Math.abs(xOf(b) - pt.x) < Math.abs(xOf(a) - pt.x) ? b : a)));
  });
  svg.addEventListener("pointerleave", hide);
  svg.addEventListener("blur", hide);
  svg.addEventListener("keydown", (ev) => {
    if (ev.key !== "ArrowLeft" && ev.key !== "ArrowRight") return;
    ev.preventDefault();
    const i = current === null ? 0 : calls.indexOf(current) + (ev.key === "ArrowRight" ? 1 : -1);
    show(calls[Math.max(0, Math.min(calls.length - 1, i))]);
  });
}

document.querySelectorAll("svg.tok-chart").forEach(attach);
