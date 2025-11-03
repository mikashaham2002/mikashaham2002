document.addEventListener('DOMContentLoaded', function () {
    let hasLoadedGraphs = false;

    // Load graphs only when user scrolls
    window.addEventListener('scroll', function () {
        if (!hasLoadedGraphs) {
            hasLoadedGraphs = true;
            loadGraphs();
        }
    });

    function loadGraphs() {
        const internetGraphsSection = document.getElementById('internet-graphs');

        if (internetGraphsSection) {
            // Add graphs within their grid style and resize them properly
            internetGraphsSection.style.display = 'grid';
            setTimeout(() => {
                const graphs = internetGraphsSection.querySelectorAll('.js-plotly-plot');
                graphs.forEach(g => Plotly.Plots.resize(g));
            }, 300);
        }
    }
});
