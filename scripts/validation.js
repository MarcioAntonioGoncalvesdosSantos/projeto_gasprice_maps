document.getElementById('searchForm').addEventListener('submit', function(event) {
    let isValid = true;

    // Validar Cidade
    const cidade = document.getElementById('cidade');
    const errorCidade = document.getElementById('error-cidade');
    if (cidade.value.trim().length > 0 && cidade.value.trim().length < 3) {
        errorCidade.style.display = 'block';
        cidade.style.borderColor = '#ef4444';
        isValid = false;
    } else {
        errorCidade.style.display = 'none';
        cidade.style.borderColor = 'rgba(255, 255, 255, 0.1)';
    }

    // Validar Raio
    const raio = document.getElementById('raio');
    const errorRaio = document.getElementById('error-raio');
    const raioValue = parseInt(raio.value);
    if (isNaN(raioValue) || raioValue < 1 || raioValue > 50) {
        errorRaio.style.display = 'block';
        raio.style.borderColor = '#ef4444';
        isValid = false;
    } else {
        errorRaio.style.display = 'none';
        raio.style.borderColor = 'rgba(255, 255, 255, 0.1)';
    }

    if (!isValid) {
        event.preventDefault();
    }
});
