console.log("GasPrice - Sistema e Banco de Dados SQLite carregados com sucesso!");

document.addEventListener('DOMContentLoaded', function() {
    // Carregar estatísticas do backend SQLite se estiver na página inicial
    const statsContainer = document.getElementById('stats-container');
    if (statsContainer) {
        carregarEstatisticas();
    }
});

function carregarEstatisticas() {
    fetch('/api/estatisticas')
        .then(response => response.json())
        .then(data => {
            if (data.combustiveis) {
                // Gasolina
                if (data.combustiveis.gasolina) {
                    document.getElementById('stat-gasolina').innerText = `R$ ${data.combustiveis.gasolina.menor.toFixed(2)}`;
                    document.getElementById('stat-gasolina-media').innerText = `Média: R$ ${data.combustiveis.gasolina.media.toFixed(2)}`;
                }
                // Etanol
                if (data.combustiveis.etanol) {
                    document.getElementById('stat-etanol').innerText = `R$ ${data.combustiveis.etanol.menor.toFixed(2)}`;
                    document.getElementById('stat-etanol-media').innerText = `Média: R$ ${data.combustiveis.etanol.media.toFixed(2)}`;
                }
                // Diesel
                if (data.combustiveis.diesel) {
                    document.getElementById('stat-diesel').innerText = `R$ ${data.combustiveis.diesel.menor.toFixed(2)}`;
                    document.getElementById('stat-diesel-media').innerText = `Média: R$ ${data.combustiveis.diesel.media.toFixed(2)}`;
                }
            }
            if (data.total_postos) {
                document.getElementById('stat-total-postos').innerText = data.total_postos;
            }
        })
        .catch(err => {
            console.error("Erro ao carregar estatísticas do SQLite:", err);
        });
}
