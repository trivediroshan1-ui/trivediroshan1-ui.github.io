/* Motion demo on the design system page */
(function(){var b=document.getElementById('mdemo'),d=document.getElementById('mdot');if(!b)return;b.addEventListener('click',function(){d.style.transition='none';d.style.transform='translateX(0)';void d.offsetWidth;d.style.transition='transform var(--hg-dur-slow) var(--hg-ease)';d.style.transform='translateX(calc(100% * 7))';});})();
