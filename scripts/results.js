document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const cidade = urlParams.get('cidade') || '';
    const combustivel = urlParams.get('combustivel') || '';
    const raio = urlParams.get('raio') || '';

    const searchInfo = document.getElementById('search-info');
    const resultsBody = document.getElementById('results-body');
    const resultsContainer = document.getElementById('results-container');
    const noResults = document.getElementById('no-results');

    let queryPath = '/api/postos?';
    if (cidade) queryPath += `cidade=${encodeURIComponent(cidade)}&`;
    if (combustivel) queryPath += `combustivel=${encodeURIComponent(combustivel)}`;

    let textoBusca = 'Exibindo todos os postos cadastrados no banco de dados';
    if (cidade && combustivel) {
        textoBusca = `Exibindo postos com <strong>${combustivel.toUpperCase()}</strong> em <strong>${cidade}</strong>`;
    } else if (cidade) {
        textoBusca = `Exibindo postos em <strong>${cidade}</strong>`;
    } else if (combustivel) {
        textoBusca = `Exibindo postos com <strong>${combustivel.toUpperCase()}</strong>`;
    }
    if (raio) {
        textoBusca += ` (Raio de busca: ~${raio}km)`;
    }

    searchInfo.innerHTML = `<p>${textoBusca}</p>`;

    fetch(queryPath)
        .then(response => response.json())
        .then(postos => {
            resultsBody.innerHTML = '';
            if (postos && postos.length > 0) {
                resultsContainer.style.display = 'block';
                noResults.style.display = 'none';

                postos.forEach((posto, index) => {
                    const row = document.createElement('tr');
                    
                    const isCheapest = index === 0 && postos.length > 1;
                    const cheapestBadge = isCheapest ? ' <span style="background: var(--gold); color: #000; font-size: 0.75rem; font-weight: 700; padding: 2px 6px; border-radius: 4px; margin-left: 6px;">MENOR PREÇO</span>' : '';

                    row.innerHTML = `
                        <td><strong>${posto.nome}</strong>${cheapestBadge}</td>
                        <td><span class="badge-bandeira">${posto.bandeira || 'Bandeira Branca'}</span></td>
                        <td>${posto.endereco}${posto.bairro ? ' (' + posto.bairro + ')' : ''}</td>
                        <td>${posto.cidade}</td>
                        <td><span class="price-tag">R$ ${parseFloat(posto.preco).toFixed(2)}</span> <span style="font-size: 0.8rem; color: var(--text-muted);">(${posto.combustivel})</span></td>
                        <td>
                            <button class="btn btn-secondary" style="padding: 0.4rem 0.8rem; font-size: 0.85rem;" onclick="abrirMapa('${posto.nome}', '${posto.endereco}', '${posto.cidade}')">
                                🗺️ Ver no Mapa
                            </button>
                        </td>
                    `;
                    resultsBody.appendChild(row);
                });
            } else {
                resultsContainer.style.display = 'none';
                noResults.style.display = 'block';
            }
        })
        .catch(err => {
            console.error("Erro ao buscar postos do SQLite:", err);
            searchInfo.innerHTML = `<p style="color: #ef4444;">Erro ao conectar com o banco de dados backend.</p>`;
            resultsContainer.style.display = 'none';
            noResults.style.display = 'block';
        });
});

function abrirMapa(nome, endereco, cidade) {
    const query = encodeURIComponent(`${nome}, ${endereco}, ${cidade}`);
    window.open(`https://www.google.com/maps/search/?api=1&query=${query}`, '_blank');
}
