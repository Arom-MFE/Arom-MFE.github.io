// Stochastic-process dividers for the home page. Each section divider is the
// mean line of a live simulated process, drawn in a 56px strip around it.
(() => {
    const CONFIG = {
        speed: 1,          // process steps per 64 ms
        scrollReveal: 0.5, // extra steps while scrolling, 0 for clock only
        amplitude: 1,      // vertical scale, 0.5 to 1.5
        showLabels: true,  // formula under each divider
        strip: 56          // strip height in px, divider at the middle
    };

    // Labels are MathML so the formulas typeset like set math: italic variables, upright ln and Poisson, real subscripts and radicals.
    const SECTIONS = [
        { id: 'home', proc: 'expou', label: '<math><mi>d</mi><mspace width="0.167em"/><mi>ln</mi><mspace width="0.167em"/><msub><mi>S</mi><mi>t</mi></msub><mo>=</mo><mi>κ</mi><mo stretchy="false">(</mo><mi>μ</mi><mo>−</mo><mi>ln</mi><mspace width="0.167em"/><msub><mi>S</mi><mi>t</mi></msub><mo stretchy="false">)</mo><mspace width="0.167em"/><mi>d</mi><mi>t</mi><mo>+</mo><mi>σ</mi><mspace width="0.167em"/><mi>d</mi><msub><mi>W</mi><mi>t</mi></msub></math>' },
        { id: 'about', proc: 'cir', label: '<math><mi>d</mi><msub><mi>r</mi><mi>t</mi></msub><mo>=</mo><mi>κ</mi><mo stretchy="false">(</mo><mi>θ</mi><mo>−</mo><msub><mi>r</mi><mi>t</mi></msub><mo stretchy="false">)</mo><mspace width="0.167em"/><mi>d</mi><mi>t</mi><mo>+</mo><mi>σ</mi><msqrt><msub><mi>r</mi><mi>t</mi></msub></msqrt><mi>d</mi><msub><mi>W</mi><mi>t</mi></msub></math>' },
        { id: 'projects', proc: 'markov', label: '<math><mi>P</mi><mo stretchy="false">(</mo><msub><mi>X</mi><mrow><mi>n</mi><mo>+</mo><mn>1</mn></mrow></msub><mo>=</mo><mi>j</mi><mo>∣</mo><msub><mi>X</mi><mi>n</mi></msub><mo>=</mo><mi>i</mi><mo stretchy="false">)</mo><mo>=</mo><msub><mi>p</mi><mrow><mi>i</mi><mi>j</mi></mrow></msub><mo>,</mo><mspace width="0.6em"/><msub><mi>p</mi><mrow><mi>i</mi><mi>j</mi></mrow></msub><mo>=</mo><mn>0</mn><mspace width="0.4em"/><mtext>for</mtext><mspace width="0.4em"/><mrow><mo stretchy="false" lspace="0" rspace="0">|</mo><mi>i</mi><mo>−</mo><mi>j</mi><mo stretchy="false" lspace="0" rspace="0">|</mo></mrow><mo>&gt;</mo><mn>1</mn></math>' },
        { id: 'experience', proc: 'jump', label: '<math><mi>d</mi><msub><mi>X</mi><mi>t</mi></msub><mo>=</mo><mrow><mo>−</mo><mi>κ</mi><msub><mi>X</mi><mi>t</mi></msub></mrow><mspace width="0.167em"/><mi>d</mi><mi>t</mi><mo>+</mo><mi>σ</mi><mspace width="0.167em"/><mi>d</mi><msub><mi>W</mi><mi>t</mi></msub><mo>+</mo><mi>J</mi><mspace width="0.167em"/><mi>d</mi><msub><mi>N</mi><mi>t</mi></msub><mo>,</mo><mspace width="0.6em"/><msub><mi>N</mi><mi>t</mi></msub><mo>∼</mo><mi>Poisson</mi><mo stretchy="false">(</mo><mi>λ</mi><mi>t</mi><mo stretchy="false">)</mo></math>' },
        { id: 'education', proc: 'heston', label: '<math><mi>d</mi><msub><mi>S</mi><mi>t</mi></msub><mo lspace="0" rspace="0">/</mo><msub><mi>S</mi><mi>t</mi></msub><mo>=</mo><msqrt><msub><mi>v</mi><mi>t</mi></msub></msqrt><mi>d</mi><msub><mi>W</mi><mi>t</mi></msub><mo>,</mo><mspace width="0.6em"/><mi>d</mi><msub><mi>v</mi><mi>t</mi></msub><mo>=</mo><mi>κ</mi><mo stretchy="false">(</mo><mi>θ</mi><mo>−</mo><msub><mi>v</mi><mi>t</mi></msub><mo stretchy="false">)</mo><mspace width="0.167em"/><mi>d</mi><mi>t</mi><mo>+</mo><mi>ξ</mi><msqrt><msub><mi>v</mi><mi>t</mi></msub></msqrt><mi>d</mi><msub><mi>Z</mi><mi>t</mi></msub><mo>,</mo><mspace width="0.6em"/><mo stretchy="false">⟨</mo><mi>d</mi><msub><mi>W</mi><mi>t</mi></msub><mo>,</mo><mi>d</mi><msub><mi>Z</mi><mi>t</mi></msub><mo stretchy="false">⟩</mo><mo>=</mo><mi>ρ</mi><mspace width="0.167em"/><mi>d</mi><mi>t</mi></math>' }
    ];

    const MATH_FONT = "math, 'STIX Two Math', 'Cambria Math', 'Latin Modern Math', 'STIXGeneral', 'Times New Roman', Times, serif";
    const s = CONFIG.amplitude;
    const lim = 22 * s;

    function gauss() {
        let u = 0;
        while (u === 0) u = Math.random();
        return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * Math.random());
    }

    // Display-only soft bound so a path never leaves the strip. The state itself is never clamped.
    function clamp(x) {
        if (x > lim) return lim - 0.35 * (x - lim);
        if (x < -lim) return -lim - 0.35 * (x + lim);
        return x;
    }

    // One column of tape is 2px. K sample paths per divider, path 0 drawn darker. Units are px per column.
    const PROC = {
        // Schwartz exponential OU on x = ln S minus its mean
        expou: {
            K: 7,
            init: () => ({ x: 0 }),
            next: (st) => {
                st.x += -0.004 * st.x + 0.9 * s * gauss();
                return clamp(st.x);
            }
        },
        // Cox-Ingersoll-Ross by Euler steps, dt = 0.02, kappa = 2.5, theta = 1, sigma = 0.5; plotted as (r - theta) * 30
        cir: {
            K: 6,
            init: () => ({ r: 1 + 0.3 * gauss() }),
            next: (st) => {
                const dt = 0.02, k = 2.5, th = 1, sg = 0.5;
                const r = Math.max(0, st.r);
                st.r = Math.abs(r + k * (th - r) * dt + sg * Math.sqrt(r * dt) * gauss());
                return clamp((st.r - th) * 30 * s);
            }
        },
        // Five-state Markov chain with a tri-diagonal transition matrix. One step is 6 columns; each chain has its own phase.
        markov: {
            K: 9,
            step: true,
            init: () => ({ k: Math.floor(Math.random() * 5), ph: Math.floor(Math.random() * 6) }),
            next: (st, col) => {
                if ((col + st.ph) % 6 === 0) {
                    const P = st.k === 0 ? [0, 0.7, 0.3] : st.k === 4 ? [0.3, 0.7, 0] : [0.15, 0.7, 0.15];
                    const u = Math.random();
                    st.k += u < P[0] ? -1 : u < P[0] + P[1] ? 0 : 1;
                }
                return (2 - st.k) * 9 * s;
            }
        },
        // OU with Poisson jumps: kappa = 0.008, sigma = 0.5, jump rate 0.007 per column, jump size 8 + 4|N|
        jump: {
            K: 6,
            init: () => ({ x: 0 }),
            next: (st) => {
                st.x += -0.008 * st.x + 0.5 * s * gauss();
                if (Math.random() < 0.007) {
                    st.x += (Math.random() < 0.5 ? -1 : 1) * (8 + 4 * Math.abs(gauss())) * s;
                }
                return clamp(st.x);
            }
        },
        // Heston, plotted as the return per column: dt = 0.03, kappa = 1, theta = 1, xi = 0.36, rho = -0.7
        heston: {
            K: 4,
            init: () => ({ v: 1 }),
            next: (st) => {
                const dt = 0.03, k = 1, th = 1, xi = 0.36, rho = -0.7;
                const v = Math.max(1e-4, st.v);
                const z1 = gauss();
                const z2 = rho * z1 + Math.sqrt(1 - rho * rho) * gauss();
                const ret = Math.sqrt(v * dt) * z1;
                st.v = Math.abs(v + k * (th - v) * dt + xi * Math.sqrt(v * dt) * z2);
                return clamp(ret * 40 * s);
            }
        }
    };

    const reduced = !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
    const tapes = [];

    // Each tape keeps a ring buffer per path; drawing walks the ring from the head so the tape flows right to left.
    function size(t) {
        const r = t.cv.getBoundingClientRect();
        const dpr = Math.min(2, window.devicePixelRatio || 1);
        const W = Math.max(64, Math.round(r.width));
        const H = Math.max(16, Math.round(r.height));
        t.cv.width = Math.round(W * dpr);
        t.cv.height = Math.round(H * dpr);
        t.ctx = t.cv.getContext('2d');
        t.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        t.W = W;
        t.H = H;
        t.dx = 2;
        t.n = Math.ceil(W / t.dx) + 2;
        t.paths = [];
        for (let i = 0; i < t.def.K; i++) {
            t.paths.push({ st: t.def.init(), a: new Float32Array(t.n) });
        }
        t.head = 0;
        t.col = 0;
        t.fade = null;
        for (let j = 0; j < t.n; j++) step(t);
        t.dirty = true;
    }

    function step(t) {
        const h = t.head;
        for (let i = 0; i < t.paths.length; i++) {
            const p = t.paths[i];
            p.a[h] = t.def.next(p.st, t.col);
        }
        t.head = (h + 1) % t.n;
        t.col++;
    }

    function draw(t, frac) {
        const c = t.ctx, W = t.W, H = t.H, n = t.n, dx = t.dx, head = t.head;
        const y0 = H / 2 - 0.5;
        const shift = frac * dx;
        const stepped = !!t.def.step;
        c.clearRect(0, 0, W, H);
        c.lineWidth = 1;
        c.lineJoin = 'round';
        c.lineCap = 'round';
        for (let p = t.paths.length - 1; p >= 0; p--) {
            const a = t.paths[p].a;
            c.strokeStyle = p === 0 ? 'rgba(0,0,0,0.30)' : 'rgba(0,0,0,0.08)';
            c.beginPath();
            let py = 0;
            for (let i = 0; i < n; i++) {
                const x = W - (n - 1 - i) * dx - shift;
                const y = y0 + a[(head + i) % n];
                if (i === 0) {
                    c.moveTo(x, y);
                } else if (stepped && y !== py) {
                    c.lineTo(x, py);
                    c.lineTo(x, y);
                } else {
                    c.lineTo(x, y);
                }
                py = y;
            }
            c.stroke();
        }
        if (stepped) {
            // faint state lattice behind the Markov chain
            c.strokeStyle = 'rgba(0,0,0,0.05)';
            c.setLineDash([2, 6]);
            c.beginPath();
            for (let k = 0; k < 5; k++) {
                if (k === 2) continue;
                const yy = Math.round(y0 + (2 - k) * 9 * s) + 0.5;
                c.moveTo(110, yy);
                c.lineTo(W, yy);
            }
            c.stroke();
            c.setLineDash([]);
        }
        if (!t.fade) {
            const g = c.createLinearGradient(0, 0, 110, 0);
            g.addColorStop(0, 'rgba(0,0,0,1)');
            g.addColorStop(1, 'rgba(0,0,0,0)');
            t.fade = g;
        }
        // fade the left edge out
        c.globalCompositeOperation = 'destination-out';
        c.fillStyle = t.fade;
        c.fillRect(0, 0, 110, H);
        c.globalCompositeOperation = 'source-over';
    }

    function mount(sec) {
        const el = document.getElementById(sec.id);
        if (!el) return;
        if (getComputedStyle(el).position === 'static') el.style.position = 'relative';
        // z-index keeps the strip and label above the next section's background
        const cv = document.createElement('canvas');
        cv.setAttribute('aria-hidden', 'true');
        cv.style.cssText = 'position:absolute;left:0;right:0;bottom:-' + (CONFIG.strip / 2) + 'px;width:100%;height:' + CONFIG.strip + 'px;z-index:1;pointer-events:none;display:block';
        el.appendChild(cv);
        if (CONFIG.showLabels) {
            const lb = document.createElement('div');
            lb.setAttribute('aria-hidden', 'true');
            lb.innerHTML = sec.label;
            lb.style.cssText = "position:absolute;right:3rem;bottom:-44px;z-index:1;font-size:12px;line-height:16px;color:#b8b8b8;white-space:nowrap;pointer-events:none";
            lb.querySelectorAll('math').forEach(m => { m.style.fontFamily = MATH_FONT; });
            el.appendChild(lb);
        }
        const t = { cv, def: PROC[sec.proc], visible: true, dirty: true };
        size(t);
        tapes.push(t);
        if ('IntersectionObserver' in window) {
            new IntersectionObserver(entries => {
                entries.forEach(e => {
                    t.visible = e.isIntersecting;
                    if (t.visible) t.dirty = true;
                });
            }, { rootMargin: '120px 0px' }).observe(cv);
        }
    }

    function init() {
        SECTIONS.forEach(mount);
        const footer = document.querySelector('footer');
        if (footer && CONFIG.showLabels) footer.style.paddingTop = '3.25rem';

        let pending = 0;
        let lastY = window.scrollY || 0;
        let acc = 0;
        let last = performance.now();
        let resizeTimer;
        window.addEventListener('scroll', () => {
            const y = window.scrollY || 0;
            pending += Math.abs(y - lastY);
            lastY = y;
        }, { passive: true });
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(() => tapes.forEach(size), 120);
        });

        // One step every 64 ms at speed 1; scrolling adds steps; only tapes near the viewport compute.
        function tick(now) {
            const elapsed = Math.min(100, now - last);
            last = now;
            const stepMs = 64 / CONFIG.speed;
            let steps = 0;
            if (!reduced) {
                acc += elapsed;
                if (CONFIG.scrollReveal > 0) {
                    const extra = Math.min(8, Math.floor(pending * CONFIG.scrollReveal / 6));
                    pending = Math.max(0, pending - extra * 6 / CONFIG.scrollReveal);
                    acc += extra * stepMs;
                }
                steps = Math.min(24, Math.floor(acc / stepMs));
                acc -= steps * stepMs;
            }
            const frac = reduced ? 0 : acc / stepMs;
            for (let i = 0; i < tapes.length; i++) {
                const t = tapes[i];
                if (!t.visible) continue;
                for (let k = 0; k < steps; k++) step(t);
                if (steps > 0 || t.dirty || frac > 0) {
                    draw(t, frac);
                    t.dirty = false;
                }
            }
            if (!reduced) requestAnimationFrame(tick);
        }
        requestAnimationFrame(tick);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
