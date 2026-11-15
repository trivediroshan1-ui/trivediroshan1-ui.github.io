/* Moved-page stub: send the reader to the new address, keeping any #section or ?query. */
(function () {
  var m = document.querySelector('meta[name="rt-moved-to"]');
  if (m) location.replace(m.content + location.search + location.hash);
})();
