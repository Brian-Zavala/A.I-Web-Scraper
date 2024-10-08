import streamlit.components.v1 as components


def brain_electrical_signals_background(num_neurons=32):
    components.html(f"""
    <style>
    body {{
        margin: 0;
        padding: 0;
        overflow: hidden;
        background-color: #000;
    }}

    #brain-electrical-signals {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -1;
    }}

    .stApp {{
        background: transparent;
    }}
    </style>
    <canvas id="brain-electrical-signals"></canvas>
    <script>
    const canvas = document.getElementById('brain-electrical-signals');
    const ctx = canvas.getContext('2d');
    let width, height;
    let neurons = [];
    const numNeurons = {num_neurons};
    const neuronRadius = 2;
    const connectionDistance = 120;
    const signalSpeed = 0.008;
    let signals = [];
    let isInteracting = false;
    let interactionTimeout;

    const fluidForce = 0.00007;
    const maxSpeed = 0.4;

    function resizeCanvas() {{
        width = window.innerWidth;
        height = window.innerHeight;
        canvas.width = width;
        canvas.height = height;
        initializeNeurons();
    }}

    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();

    function getRandomColor() {{
        const r = Math.floor(Math.random() * 256);
        const g = Math.floor(Math.random() * 256);
        const b = Math.floor(Math.random() * 256);
        return `rgb(${{r}},${{g}},${{b}})`;
    }}

    function initializeNeurons() {{
        neurons = [];
        for (let i = 0; i < numNeurons; i++) {{
            neurons.push({{
                x: Math.random() * width,
                y: Math.random() * height,
                vx: (Math.random() - 0.5) * maxSpeed,
                vy: (Math.random() - 0.5) * maxSpeed,
                color: getRandomColor(),
                activated: false,
                activationTime: 0
            }});
        }}
    }}

    function updateNeuronPositions(time) {{
        neurons.forEach(neuron => {{
            neuron.vx += (Math.random() - 0.5) * fluidForce;
            neuron.vy += (Math.random() - 0.5) * fluidForce;

            const speed = Math.sqrt(neuron.vx * neuron.vx + neuron.vy * neuron.vy);
            if (speed > maxSpeed) {{
                neuron.vx = (neuron.vx / speed) * maxSpeed;
                neuron.vy = (neuron.vy / speed) * maxSpeed;
            }}

            neuron.x += neuron.vx;
            neuron.y += neuron.vy;

            if (neuron.x < 0) neuron.x = width;
            if (neuron.x > width) neuron.x = 0;
            if (neuron.y < 0) neuron.y = height;
            if (neuron.y > height) neuron.y = 0;
        }});
    }}

    function drawNeurons() {{
        neurons.forEach(neuron => {{
            ctx.fillStyle = neuron.color;
            ctx.beginPath();
            ctx.arc(neuron.x, neuron.y, neuronRadius, 0, Math.PI * 2);
            ctx.fill();
        }});
    }}

    function createZigZagPath(x1, y1, x2, y2, segments = 12) {{
        const path = [];
        const zigzagScale = 0.15;

        for (let i = 0; i <= segments; i++) {{
            const t = i / segments;
            const x = x1 + (x2 - x1) * t;
            const y = y1 + (y2 - y1) * t;

            const perpX = -(y2 - y1) * zigzagScale;
            const perpY = (x2 - x1) * zigzagScale;

            const zigzag = Math.sin(t * Math.PI * 6) * (1 - t);

            path.push({{ 
                x: x + perpX * zigzag, 
                y: y + perpY * zigzag 
            }});
        }}
        return path;
    }}

    function drawFlowingElectricity(signal, currentTime) {{
        const progress = Math.min(1, (currentTime - signal.startTime) * signalSpeed);
        const numPoints = Math.floor(progress * signal.path.length);

        const gradient = ctx.createLinearGradient(
            signal.path[0].x, signal.path[0].y,
            signal.path[signal.path.length - 1].x, signal.path[signal.path.length - 1].y
        );
        gradient.addColorStop(0, 'rgba(0, 255, 255, 0.8)');
        gradient.addColorStop(0.5, 'rgba(255, 0, 255, 0.8)');
        gradient.addColorStop(1, 'rgba(255, 255, 0, 0.8)');

        ctx.strokeStyle = gradient;
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(signal.path[0].x, signal.path[0].y);

        for (let i = 1; i < numPoints; i++) {{
            ctx.lineTo(signal.path[i].x, signal.path[i].y);
        }}

        ctx.stroke();

        // Add glow effect
        ctx.shadowBlur = 5;
        ctx.shadowColor = 'rgba(255, 255, 255, 0.5)';
        ctx.stroke();
        ctx.shadowBlur = 0;

        return progress < 1;
    }}

    function animate(currentTime) {{
        ctx.clearRect(0, 0, width, height);
        updateNeuronPositions(currentTime);
        drawNeurons();

        signals = signals.filter(signal => drawFlowingElectricity(signal, currentTime));

        if (isInteracting) {{
            const nearbyNeurons = getNearbyNeurons(lastInteractionPos.x, lastInteractionPos.y, connectionDistance);
            if (nearbyNeurons.length > 1) {{
                const numSourceNeurons = Math.min(4, nearbyNeurons.length);
                for (let s = 0; s < numSourceNeurons; s++) {{
                    const sourceNeuron = nearbyNeurons[s];
                    for (let i = 0; i < nearbyNeurons.length; i++) {{
                        if (i !== s) {{
                            const targetNeuron = nearbyNeurons[i];
                            if (Math.random() < 0.1) {{  // Increased probability for more signals
                                signals.push({{
                                    path: createZigZagPath(sourceNeuron.x, sourceNeuron.y, targetNeuron.x, targetNeuron.y),
                                    startTime: currentTime
                                }});
                            }}
                        }}
                    }}
                }}
            }}
        }}

        requestAnimationFrame(animate);
    }}

    function getNearbyNeurons(x, y, maxDistance) {{
        return neurons.filter(neuron => {{
            const dx = neuron.x - x;
            const dy = neuron.y - y;
            return Math.sqrt(dx * dx + dy * dy) < maxDistance;
        }});
    }}

    let lastInteractionPos = {{ x: null, y: null }};

    function startInteraction(x, y) {{
        isInteracting = true;
        lastInteractionPos = {{ x, y }};
        clearTimeout(interactionTimeout);
    }}

    function stopInteraction() {{
        interactionTimeout = setTimeout(() => {{
            isInteracting = false;
            lastInteractionPos = {{ x: null, y: null }};
        }}, 100);
    }}

    function onInteraction(event) {{
        const rect = canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        startInteraction(x, y);
    }}

    canvas.addEventListener('mousemove', onInteraction);
    canvas.addEventListener('mouseout', stopInteraction);
    canvas.addEventListener('touchmove', (e) => {{
        e.preventDefault();
        onInteraction(e.touches[0]);
    }});
    canvas.addEventListener('touchstart', (e) => {{
        e.preventDefault();
        onInteraction(e.touches[0]);
    }});
    canvas.addEventListener('touchend', stopInteraction);

    initializeNeurons();
    requestAnimationFrame(animate);
    </script>
    """)
