import streamlit.components.v1 as components


def interactive_background(num_nodes=20, node_color='rgb(0, 0, 0)', connection_color='rgb(255, 255, 255)'):
    components.html(f"""
        <style>
        #ai-neural-network {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            z-index: -1;
            pointer-events: none;
        }}
        </style>
        <canvas id="ai-neural-network"></canvas>
        <script>
        const canvas = document.getElementById('ai-neural-network');
        const ctx = canvas.getContext('2d');
        let width, height;
        let nodes = [];
        const numNodes = {num_nodes};
        let mouse = {{ x: null, y: null, radius: 150 }};

        function resizeCanvas() {{
            width = window.innerWidth;
            height = window.innerHeight;
            canvas.width = width;
            canvas.height = height;
        }}

        window.addEventListener('resize', resizeCanvas);
        resizeCanvas();

        class Node {{
            constructor() {{
                this.x = Math.random() * width;
                this.y = Math.random() * height;
                this.radius = Math.random() * 4 + 2;
                this.speedX = Math.random() * 1 - 0.5;
                this.speedY = Math.random() * 1 - 0.5;
            }}

            update() {{
                this.x += this.speedX;
                this.y += this.speedY;

                if (this.x > width + this.radius) {{
                    this.x = -this.radius;
                }} else if (this.x < -this.radius) {{
                    this.x = width + this.radius;
                }}
                if (this.y > height + this.radius) {{
                    this.y = -this.radius;
                }} else if (this.y < -this.radius) {{
                    this.y = height + this.radius;
                }}

                if (mouse.x && mouse.y) {{
                    const dx = mouse.x - this.x;
                    const dy = mouse.y - this.y;
                    const distance = Math.sqrt(dx * dx + dy * dy);
                    if (distance < mouse.radius) {{
                        const angle = Math.atan2(dy, dx);
                        this.x -= Math.cos(angle) * 3;
                        this.y -= Math.sin(angle) * 3;
                    }}
                }}
            }}

            draw() {{
                ctx.fillStyle = '{node_color}';
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                ctx.fill();
            }}
        }}

        function init() {{
            nodes = [];
            for (let i = 0; i < numNodes; i++) {{
                nodes.push(new Node());
            }}
        }}

        function animate() {{
            ctx.clearRect(0, 0, width, height);
            for (let i = 0; i < nodes.length; i++) {{
                nodes[i].update();
                nodes[i].draw();
                connectNodes(nodes[i], nodes);
            }}
            requestAnimationFrame(animate);
        }}

        function connectNodes(node, nodes) {{
            for (let j = 0; j < nodes.length; j++) {{
                const dx = node.x - nodes[j].x;
                const dy = node.y - nodes[j].y;
                const distance = Math.sqrt(dx * dx + dy * dy);

                if (distance < 150) {{
                    ctx.strokeStyle = '{connection_color}';
                    ctx.lineWidth = 0.2;
                    ctx.beginPath();
                    ctx.moveTo(node.x, node.y);
                    ctx.lineTo(nodes[j].x, nodes[j].y);
                    ctx.stroke();
                }}
            }}
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