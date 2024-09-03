import streamlit.components.v1 as components
import random


def brain_electrical_signals_background(num_signals=50, signal_color='rgba(255, 255, 255, 0.8)',
                                        pulse_color='rgb(255, 0, 238)', spark_color='rgba(255, 255, 255, 0.8)',
                                        lightning_color='rgba(255, 255, 255, 0.8)'):
    components.html(f"""
    <style>
    body {{
        margin: 0;
        padding: 0;
        overflow: hidden;
    }}

    #brain-electrical-signals {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -1;
        pointer-events: none;
    }}

    .stApp {{
        position: relative;
        z-index: 1;
    }}
    </style>
    <canvas id="brain-electrical-signals"></canvas>
    <script>
    const canvas = document.getElementById('brain-electrical-signals');
    const ctx = canvas.getContext('2d');
    let width, height;
    let signals = [];
    let sparks = [];
    let lightningBolts = [];
    const numSignals = {num_signals};
    let mouse = {{ x: null, y: null, radius: 100 }};
    let isSmallScreen = window.innerWidth < 768;
    let isMobileDevice = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    let lastInteractionTime = 0;
    const mobileVisibleTime = 500; // 500ms visible time for mobile
    const mobileDecayTime = 300; // 300ms decay time for mobile

    function resizeCanvas() {{
        width = window.innerWidth;
        height = window.innerHeight;
        canvas.width = width;
        canvas.height = height;
        isSmallScreen = window.innerWidth < 768;
    }}

    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();

    class Signal {{
        constructor(x, y) {{
            this.x = x;
            this.y = y;
            this.speedX = Math.random() * 3 - 1.5;
            this.speedY = Math.random() * 3 - 1.5;
            this.lifetime = Math.random() * 200 + 50;
            this.initialLifetime = this.lifetime;
            this.pulsing = false;
        }}

        update(currentTime) {{
            this.x += this.speedX;
            this.y += this.speedY;

            if (this.x > width || this.x < 0) {{
                this.speedX *= -1;
            }}
            if (this.y > height || this.y < 0) {{
                this.speedY *= -1;
            }}

            if (mouse.x && mouse.y) {{
                const dx = mouse.x - this.x;
                const dy = mouse.y - this.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                if (distance < mouse.radius) {{
                    this.pulsing = true;
                    sparks.push(new Spark(this.x, this.y));
                    lightningBolts.push(new LightningBolt(this.x, this.y));
                }}
            }}

            if (this.pulsing) {{
                if (isMobileDevice) {{
                    const timeSinceInteraction = currentTime - lastInteractionTime;
                    if (timeSinceInteraction > mobileVisibleTime) {{
                        const decayProgress = Math.min(1, (timeSinceInteraction - mobileVisibleTime) / mobileDecayTime);
                        this.lifetime -= 2 * decayProgress;
                    }}
                }} else {{
                    this.lifetime -= 2;
                }}
            }} else {{
                this.lifetime -= 1;
            }}

            if (this.lifetime <= 0) {{
                this.x = Math.random() * width;
                this.y = Math.random() * height;
                this.lifetime = this.initialLifetime;
                this.pulsing = false;
            }}
        }}

        draw() {{
            const opacity = this.lifetime / this.initialLifetime;
            if (this.pulsing) {{
                ctx.strokeStyle = '{pulse_color}';
            }} else {{
                ctx.strokeStyle = `${{'{signal_color}'.slice(0, -4)}}${{opacity}})`;
            }}
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(this.x, this.y);
            ctx.lineTo(this.x + this.speedX * 10, this.y + this.speedY * 10);
            ctx.stroke();
        }}
    }}

    class Spark {{
        constructor(x, y) {{
            this.x = x;
            this.y = y;
            this.speedX = Math.random() * 6 - 3;
            this.speedY = Math.random() * 6 - 3;
            this.size = Math.random() * 4 + 1;
            this.lifetime = isMobileDevice ? mobileVisibleTime + mobileDecayTime : Math.random() * 30 + 10;
            this.trailLength = Math.random() * 20 + 5;
            this.trail = [];
        }}

        update(currentTime) {{
            this.x += this.speedX;
            this.y += this.speedY;
            this.size *= 0.95;

            if (isMobileDevice) {{
                const timeSinceInteraction = currentTime - lastInteractionTime;
                if (timeSinceInteraction > mobileVisibleTime) {{
                    const decayProgress = Math.min(1, (timeSinceInteraction - mobileVisibleTime) / mobileDecayTime);
                    this.lifetime = mobileVisibleTime + mobileDecayTime - (decayProgress * mobileDecayTime);
                }}
            }} else {{
                this.lifetime -= 1;
            }}

            this.trail.push({{ x: this.x, y: this.y }});
            if (this.trail.length > this.trailLength) {{
                this.trail.shift();
            }}
        }}

        draw() {{
            const opacity = this.lifetime / (isMobileDevice ? (mobileVisibleTime + mobileDecayTime) : 30);
            ctx.fillStyle = `${{'{spark_color}'.slice(0, -4)}}${{opacity}})`;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();

            ctx.strokeStyle = `${{'{spark_color}'.slice(0, -4)}}${{opacity}})`;
            ctx.lineWidth = this.size;
            ctx.beginPath();
            ctx.moveTo(this.trail[0].x, this.trail[0].y);
            for (let i = 1; i < this.trail.length; i++) {{
                ctx.lineTo(this.trail[i].x, this.trail[i].y);
            }}
            ctx.stroke();
        }}

        isAlive() {{
            return this.lifetime > 0;
        }}
    }}

    class LightningBolt {{
        constructor(x, y) {{
            this.x = x;
            this.y = y;
            this.branches = [];
            this.lifetime = isMobileDevice ? mobileVisibleTime + mobileDecayTime : (isSmallScreen ? 2 : Math.random() * 20 + 10);
            this.createBranches();
        }}

        createBranches() {{
            const numBranches = Math.random() * 2 + 1;
            for (let i = 0; i < numBranches; i++) {{
                const branch = {{
                    x: this.x,
                    y: this.y,
                    points: [],
                    color: `${{'{lightning_color}'.slice(0, -4)}}${{Math.random() * 0.3 + 0.2}})`
                }};

                const numPoints = Math.random() * 3 + 2;
                for (let j = 0; j < numPoints; j++) {{
                    const offsetX = Math.random() * 100 - 50;
                    const offsetY = Math.random() * 100 - 50;
                    branch.points.push({{ x: branch.x + offsetX, y: branch.y + offsetY }});
                    branch.x += offsetX;
                    branch.y += offsetY;
                }}

                this.branches.push(branch);
            }}
        }}

        update(currentTime) {{
            if (isMobileDevice) {{
                const timeSinceInteraction = currentTime - lastInteractionTime;
                if (timeSinceInteraction > mobileVisibleTime) {{
                    const decayProgress = Math.min(1, (timeSinceInteraction - mobileVisibleTime) / mobileDecayTime);
                    this.lifetime = mobileVisibleTime + mobileDecayTime - (decayProgress * mobileDecayTime);
                }}
            }} else {{
                this.lifetime -= 1;
            }}
        }}

        draw() {{
            const opacity = isMobileDevice ? this.lifetime / (mobileVisibleTime + mobileDecayTime) : 
                            (isSmallScreen ? this.lifetime / 2 : this.lifetime / 20);
            for (let i = 0; i < this.branches.length; i++) {{
                const branch = this.branches[i];
                ctx.strokeStyle = branch.color.replace('0.5', opacity);
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.moveTo(branch.points[0].x, branch.points[0].y);
                for (let j = 1; j < branch.points.length; j++) {{
                    ctx.lineTo(branch.points[j].x, branch.points[j].y);
                }}
                ctx.stroke();
            }}
        }}

        isAlive() {{
            return this.lifetime > 0;
        }}
    }}

    function init() {{
        signals = [];
        for (let i = 0; i < numSignals; i++) {{
            const x = Math.random() * width;
            const y = Math.random() * height;
            signals.push(new Signal(x, y));
        }}
    }}

    function animate(currentTime) {{
        ctx.clearRect(0, 0, width, height);
        for (let i = 0; i < signals.length; i++) {{
            signals[i].update(currentTime);
            signals[i].draw();
        }}

        for (let i = sparks.length - 1; i >= 0; i--) {{
            sparks[i].update(currentTime);
            sparks[i].draw();
            if (!sparks[i].isAlive()) {{
                sparks.splice(i, 1);
            }}
        }}

        for (let i = lightningBolts.length - 1; i >= 0; i--) {{
            lightningBolts[i].update(currentTime);
            lightningBolts[i].draw();
            if (!lightningBolts[i].isAlive()) {{
                lightningBolts.splice(i, 1);
            }}
        }}

        requestAnimationFrame(animate);
    }}

    function handleInteraction(event) {{
        lastInteractionTime = performance.now();
        const rect = canvas.getBoundingClientRect();
        const x = (event.clientX || event.touches[0].clientX) - rect.left;
        const y = (event.clientY || event.touches[0].clientY) - rect.top;
        mouse.x = x;
        mouse.y = y;
    }}

    document.addEventListener('mousemove', handleInteraction);
    document.addEventListener('touchmove', handleInteraction);
    document.addEventListener('touchstart', handleInteraction);

    document.addEventListener('mouseleave', () => {{
        mouse.x = null;
        mouse.y = null;
    }});

    document.addEventListener('touchend', () => {{
        mouse.x = null;
        mouse.y = null;
    }});

    init();
    requestAnimationFrame(animate);
    </script>
    """)