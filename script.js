function toggleTheme(){
  const isLight = document.documentElement.classList.toggle('light');
  document.getElementById('themeToggle').textContent = isLight ? '☀️' : '🌙';
  try { localStorage.setItem('theme', isLight ? 'light' : 'dark'); } catch(e) {}
}
document.addEventListener('DOMContentLoaded', () => {
  if (document.documentElement.classList.contains('light')) {
    const btn = document.getElementById('themeToggle');
    if (btn) btn.textContent = '☀️';
  }
});
/* Project filters.
   These buttons used to only move the .active class around, so they looked
   clickable and did nothing. Each .project-card carries a data-category and
   each button a data-filter; "all" shows everything. Counts are derived from
   the cards actually present rather than hard-coded, so they can't drift out
   of sync with the grid when the sync workflow appends a new card. */
(function(){
  const buttons = document.querySelectorAll('.filter-btn[data-filter]');
  const cards = document.querySelectorAll('.project-card[data-category]');
  if (!buttons.length || !cards.length) return;

  buttons.forEach(btn => {
    const filter = btn.dataset.filter;
    const countEl = btn.querySelector('.filter-count');
    if (countEl) {
      countEl.textContent = filter === 'all'
        ? cards.length
        : Array.from(cards).filter(c => c.dataset.category === filter).length;
    }

    btn.addEventListener('click', () => {
      buttons.forEach(b => {
        b.classList.remove('active');
        b.setAttribute('aria-pressed', 'false');
      });
      btn.classList.add('active');
      btn.setAttribute('aria-pressed', 'true');
      cards.forEach(card => {
        const show = filter === 'all' || card.dataset.category === filter;
        card.hidden = !show;
      });
    });
  });

  // Hide any filter with nothing behind it, so you can't land on an empty grid.
  buttons.forEach(btn => {
    const filter = btn.dataset.filter;
    if (filter === 'all') return;
    const n = Array.from(cards).filter(c => c.dataset.category === filter).length;
    if (n === 0) btn.hidden = true;
  });
})();
function tick(){
  const now = new Date();
  const el = document.getElementById('clock');
  if (el) el.textContent = now.toLocaleTimeString('en-NZ',{hour12:false}) + ' NZST';
}
tick(); setInterval(tick,1000);
