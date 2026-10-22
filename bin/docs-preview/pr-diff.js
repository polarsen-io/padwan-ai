// Injected into changed PR-preview pages by mark_changes.py: toggle highlights, jump between changes.
document.querySelectorAll('.pr-diff-bar [data-toggle]').forEach((b) =>
  b.addEventListener('click', () => {
    const off = document.documentElement.classList.toggle('pr-diff-off');
    b.textContent = off ? 'show changes' : 'hide changes';
  }),
);
document.querySelectorAll('.pr-diff-bar [data-next]').forEach((b) => {
  let i = -1;
  b.addEventListener('click', () => {
    const marks = document.querySelectorAll('[data-pr-diff]');
    if (!marks.length) return;
    i = (i + 1) % marks.length;
    marks[i].scrollIntoView({ block: 'center', behavior: 'smooth' });
  });
});
