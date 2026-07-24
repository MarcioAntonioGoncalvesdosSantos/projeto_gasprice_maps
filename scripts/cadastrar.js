document.getElementById('cadastrarForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const data = {
        nome: document.getElementById('nome').value.trim(),
        bandeira: document.getElementById('bandeira').value,
        cidade: document.getElementById('cidade').value.trim(),
        bairro: document.getElementById('bairro').value.trim(),
        endereco: document.getElementById('endereco').value.trim(),
        combustivel: document.getElementById('combustivel').value,
        preco: parseFloat(document.getElementById('preco').value)
    };

    fetch('/api/postos', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.status === 'success') {
            showToast('✅ Preço cadastrado com sucesso no banco de dados SQLite!');
            document.getElementById('cadastrarForm').reset();
            setTimeout(() => {
                window.location.href = `formAction.html?cidade=${encodeURIComponent(data.cidade)}&combustivel=${data.combustivel}`;
            }, 1800);
        } else {
            showToast('❌ Erro: ' + (result.error || 'Não foi possível salvar.'));
        }
    })
    .catch(err => {
        console.error('Erro na requisição:', err);
        showToast('❌ Erro ao conectar ao servidor backend.');
    });
});

function showToast(message) {
    const toast = document.getElementById('toast');
    toast.innerText = message;
    toast.style.display = 'block';
    setTimeout(() => {
        toast.style.display = 'none';
    }, 3500);
}
