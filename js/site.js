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
