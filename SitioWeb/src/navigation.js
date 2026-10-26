(() => {
  const key = path => `portfolio:reading-position:${path}`;

  // Save the point of departure only for navigation in this tab.
  document.addEventListener('click', event => {
    const link = event.target.closest('a[href]');
    if (!link || event.defaultPrevented || event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey || link.target === '_blank' || link.hasAttribute('download')) return;
    const destination = new URL(link.href, location.href);
    if (destination.origin !== location.origin || destination.pathname === location.pathname) return;
    try {
      const heading = [...document.querySelectorAll('.reading h1[id], .reading h2[id], .reading h3[id], .reading h4[id]')]
        .filter(item => item.getBoundingClientRect().top <= 120).pop();
      sessionStorage.setItem(key(location.pathname), JSON.stringify({
        y: window.scrollY,
        heading: heading?.id,
        offset: heading ? -heading.getBoundingClientRect().top : 0,
      }));
      if (link.hasAttribute('data-return-report')) {
        destination.searchParams.set('volver', '1');
        link.href = destination.href;
      }
    } catch {
      // Navigation still works if browser storage is unavailable.
    }
  });

  const current = new URL(location.href);
  if (current.searchParams.get('volver') !== '1') return;
  current.searchParams.delete('volver');
  history.replaceState(history.state, '', current.href);
  try {
    const saved = JSON.parse(sessionStorage.getItem(key(location.pathname)) || 'null');
    if (!saved || !Number.isFinite(saved.y)) return;
    requestAnimationFrame(() => requestAnimationFrame(() => {
      const heading = saved.heading && document.getElementById(saved.heading);
      const y = heading ? heading.getBoundingClientRect().top + window.scrollY + saved.offset : saved.y;
      window.scrollTo({top: y, behavior: 'instant'});
    }));
  } catch {
    // Direct visits without a saved position retain normal navigation.
  }
})();
