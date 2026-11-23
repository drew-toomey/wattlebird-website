// One place to set each outside link. Leave empty and those buttons hide themselves.
var STEAM_URL = "";
var DISCORD_URL = "https://discord.gg/7C2AYfKsSu";
function wire(attr, url) {
  document.querySelectorAll("[" + attr + "]").forEach(function (a) {
    if (url) { a.href = url; a.target = "_blank"; a.rel = "noopener"; } else { a.remove(); }
  });
}
wire("data-steam", STEAM_URL);
wire("data-discord", DISCORD_URL);
document.querySelectorAll("[data-year]").forEach(function (s) { s.textContent = new Date().getFullYear(); });
// Blog "Copy link" buttons
document.querySelectorAll("[data-copy]").forEach(function (a) {
  a.addEventListener("click", function (e) {
    e.preventDefault();
    try { navigator.clipboard.writeText(a.getAttribute("data-copy")); a.textContent = "Copied!"; } catch (err) { prompt("Copy this link", a.getAttribute("data-copy")); }
  });
});
