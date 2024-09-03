import streamlit.components.v1 as components
import random


def brain_electrical_signals_background(num_signals=34, signal_color='rgba(255, 255, 255, 0.8)',
                                        pulse_color='rgba(255, 255, 0, 0.8)', spark_color='rgba(255, 255, 255, 0.8)'):
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
    const numSignals = {num_signals};
    let mouse = {{ x: null, y: null, radius: 100 }};

    function resizeCanvas() {{
        width = window.innerWidth;
        height = window.innerHeight;
        canvas.width = width;
        canvas.height = height;
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

        update() {{
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
                }}
            }}

            if (this.pulsing) {{
                this.lifetime -= 2;
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
            this.speedX = Math.random() * 4 - 2;
            this.speedY = Math.random() * 4 - 2;
            this.size = Math.random() * 3 + 1;
            this.lifetime = Math.random() * 20 + 10;
        }}

        update() {{
            this.x += this.speedX;
            this.y += this.speedY;
            this.size *= 0.95;
            this.lifetime -= 1;
        }}

        draw() {{
            const opacity = this.lifetime / 20;
            ctx.fillStyle = `${{'{spark_color}'.slice(0, -4)}}${{opacity}})`;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();
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

    function animate() {{
        ctx.clearRect(0, 0, width, height);
        for (let i = 0; i < signals.length; i++) {{
            signals[i].update();
            signals[i].draw();
        }}

        for (let i = sparks.length - 1; i >= 0; i--) {{
            sparks[i].update();
            sparks[i].draw();
            if (!sparks[i].isAlive()) {{
                sparks.splice(i, 1);
            }}
        }}

        requestAnimationFrame(animate);
    }}

    document.addEventListener('mousemove', (event) => {{
        mouse.x = event.clientX;
        mouse.y = event.clientY;
    }});

    document.addEventListener('mouseleave', () => {{
        mouse.x = null;
        mouse.y = null;
    }});

    init();
    animate();
    </script>
    """)