const cursor = document.getElementById('cursor');
const ring = document.getElementById('cursorRing');
let mx=0, my=0, rx=0, ry=0;

document.addEventListener('mousemove', e => {
  mx = e.clientX;
  my = e.clientY;
  cursor.style.left = mx + 'px';
  cursor.style.top = my + 'px';
});

(function animate(){
  rx += (mx - rx) * 0.15;
  ry += (my - ry) * 0.15;
  ring.style.left = rx + 'px';
  ring.style.top = ry + 'px';
  requestAnimationFrame(animate);
})();

document.querySelectorAll('a, button, .module-card, .role-card').forEach(el => {
  el.addEventListener('mouseenter', () => {
    ring.style.width = '60px';
    ring.style.height = '60px';
    ring.style.background = 'rgba(255, 193, 7, 0.1)';
  });
  el.addEventListener('mouseleave', () => {
    ring.style.width = '36px';
    ring.style.height = '36px';
    ring.style.background = 'transparent';
  });
});
function handleLogin() {
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;

  // Basic validation
  if (!email || !password) {
      showToast("Please enter your credentials");
      return;
  }

  // Logic to determine where they go
  // In a real app, this data comes from your database/backend
  if (targetPage === 'staff-dashboard.html') {
      // Redirect to a role selection portal instead of a generic dashboard
      window.location.href = 'staff-role-selection.html';
  } else {
      window.location.href = 'student-dashboard.html';
  }
}
window.addEventListener('scroll',()=>{ document.getElementById('navbar').classList.toggle('scrolled',scrollY>50); });
const observer=new IntersectionObserver(e=>{e.forEach(x=>{if(x.isIntersecting)x.target.classList.add('visible')})},{threshold:0.1});
document.querySelectorAll('.reveal').forEach(el=>observer.observe(el));