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
document.querySelectorAll('.filter-btn').forEach(btn=>{
  btn.addEventListener('click', ()=>{
    document.querySelectorAll('.filter-btn').forEach(b=>b.classList.remove('active'));
    btn.classList.add('active');
  });
});
function tick(){
  const now = new Date();
  const el = document.getElementById('clock');
  if (el) el.textContent = now.toLocaleTimeString('en-NZ',{hour12:false}) + ' NZST';
}
tick(); setInterval(tick,1000);
