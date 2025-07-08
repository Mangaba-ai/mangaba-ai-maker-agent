document.addEventListener('DOMContentLoaded', () => {
    // Seletores de elementos
    const steps = { 1: document.getElementById('step-1'), 2: document.getElementById('step-2'), 3: document.getElementById('step-3') };
    const progressBar = document.querySelector('#progress-wizard .progress-bar');
    const btnStep1 = document.getElementById('btn-step-1');
    const btnBack2 = document.getElementById('btn-back-2');
    const btnStep2 = document.getElementById('btn-step-2');
    const btnCopy = document.getElementById('btn-copy');
    const btnReset = document.getElementById('btn-reset');
    const goalInput = document.getElementById('goalInput');
    const goalValidation = document.getElementById('goal-validation');
    const dataSourceInput = document.getElementById('dataSource');
    const fileLabel = document.getElementById('file-label');
    const jsonInput = document.getElementById('jsonInput');
    const exampleSelect = document.getElementById('exampleSelect');
    const examplePreview = document.getElementById('example-preview');
    const exampleContent = document.getElementById('example-content');
    const fileInputSection = document.getElementById('file-input-section');
    const jsonInputSection = document.getElementById('json-input-section');
    const exampleInputSection = document.getElementById('example-input-section');
    const dataSourceTypeRadios = document.querySelectorAll('input[name="dataSourceType"]');
    const liveLog = document.getElementById('live-log');
    const resultContent = document.getElementById('result-content');
    const backToTopBtn = document.getElementById('back-to-top');

    // Mapeamento de nomes de exemplo para nomes de arquivo
    const exampleFileMap = {
        produtos: 'produtos.json',
        usuarios: 'usuarios.json',
        vendas: 'vendas.json',
        tarefas: 'tarefas.json',
        planejamento_estrategico: 'planejamento_estrategico.json',
        analise_concorrencia: 'analise_concorrencia.json',
        okrs_planejamento: 'okrs_planejamento.json',
        burger_king_brasil: 'burger_king_brasil.json'
    };

    // Navegação entre os passos
    const navigateToStep = (step) => {
        Object.values(steps).forEach(s => s.classList.add('d-none'));
        const currentStep = steps[step];
        currentStep.classList.remove('d-none', 'animated');
        void currentStep.offsetWidth;
        currentStep.classList.add('animated');

        const progress = (step / 3) * 100;
        progressBar.style.width = `${progress}%`;
        progressBar.setAttribute('aria-valuenow', progress);
    };

    // Event Listeners
    btnStep1.addEventListener('click', () => {
        if (!goalInput.value.trim()) {
            goalValidation.classList.remove('d-none');
            return;
        }
        goalValidation.classList.add('d-none');
        navigateToStep(2);
    });

    btnBack2.addEventListener('click', () => navigateToStep(1));

    btnStep2.addEventListener('click', async () => {
        const btnText = btnStep2.querySelector('.btn-text');
        const spinner = btnStep2.querySelector('.spinner-border');
        spinner.classList.remove('d-none');
        btnStep2.disabled = true;
        btnText.textContent = 'Processando...';

        navigateToStep(3);
        await runAgentSystem();

        spinner.classList.add('d-none');
        btnStep2.disabled = false;
        btnText.textContent = 'Iniciar Sistema';
    });

    btnReset.addEventListener('click', () => {
        goalInput.value = '';
        dataSourceInput.value = '';
        jsonInput.value = '';
        exampleSelect.value = '';
        fileLabel.innerHTML = '<i class="bi bi-upload"></i> Clique para selecionar um arquivo';
        examplePreview.classList.add('d-none');
        liveLog.innerHTML = '';
        resultContent.innerHTML = '<div class="placeholder-glow"><span class="placeholder col-7"></span><span class="placeholder col-4"></span><span class="placeholder col-4"></span><span class="placeholder col-6"></span><span class="placeholder col-8"></span></div>';
        navigateToStep(1);
    });

    btnCopy.addEventListener('click', () => {
        navigator.clipboard.writeText(resultContent.innerText).then(() => {
            const originalText = btnCopy.innerHTML;
            btnCopy.innerHTML = '<i class="bi bi-check-lg"></i> Copiado!';
            setTimeout(() => { btnCopy.innerHTML = originalText; }, 2000);
        });
    });

    dataSourceTypeRadios.forEach(radio => {
        radio.addEventListener('change', () => {
            fileInputSection.classList.toggle('d-none', radio.value !== 'file');
            jsonInputSection.classList.toggle('d-none', radio.value !== 'json');
            exampleInputSection.classList.toggle('d-none', radio.value !== 'example');
        });
    });

    dataSourceInput.addEventListener('change', () => {
        fileLabel.textContent = dataSourceInput.files.length > 0 ? dataSourceInput.files[0].name : 'Clique para selecionar um arquivo';
    });

    exampleSelect.addEventListener('change', async () => {
        const selectedExampleKey = exampleSelect.value;
        const filename = exampleFileMap[selectedExampleKey];

        if (filename) {
            try {
                const response = await fetch(`/data/${filename}`);
                if (!response.ok) throw new Error(`Erro ao carregar o exemplo: ${response.statusText}`);
                const data = await response.json();
                exampleContent.textContent = JSON.stringify(data, null, 2);
                examplePreview.classList.remove('d-none');
            } catch (error) {
                console.error('Erro ao carregar exemplo JSON:', error);
                exampleContent.textContent = `Erro ao carregar o exemplo: ${error.message}`;
                examplePreview.classList.remove('d-none');
            }
        } else {
            examplePreview.classList.add('d-none');
        }
    });

    // Lógica do sistema de agentes
    const runAgentSystem = async () => {
        clearResults();
        const formData = new FormData();
        formData.append('goal', goalInput.value);

        const selectedDataSourceType = document.querySelector('input[name="dataSourceType"]:checked').value;
        if (selectedDataSourceType === 'file' && dataSourceInput.files.length > 0) {
            formData.append('dataSource', dataSourceInput.files[0]);
        } else if (selectedDataSourceType === 'json' && jsonInput.value.trim()) {
            formData.append('json_data', jsonInput.value);
        } else if (selectedDataSourceType === 'example' && exampleSelect.value) {
            // Para exemplos, buscamos o conteúdo do arquivo e o enviamos como json_data
            const selectedExampleKey = exampleSelect.value;
            const filename = exampleFileMap[selectedExampleKey];
            if (filename) {
                try {
                    const response = await fetch(`/data/${filename}`);
                    if (!response.ok) throw new Error(`Erro ao carregar o exemplo: ${response.statusText}`);
                    const data = await response.json();
                    formData.append('json_data', JSON.stringify(data));
                } catch (error) {
                    console.error('Erro ao preparar exemplo para envio:', error);
                    alert('Não foi possível carregar o exemplo selecionado. Tente novamente.');
                    return; // Impede o envio se o exemplo não puder ser carregado
                }
            }
        }

        try {
            const response = await fetch('/api/run_agent_system', { method: 'POST', body: formData });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Erro no servidor');
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                buffer += decoder.decode(value, { stream: true });

                // Processar eventos completos no buffer
                let newlineIndex;
                while ((newlineIndex = buffer.indexOf('\n\n')) !== -1) {
                    const eventString = buffer.substring(0, newlineIndex);
                    buffer = buffer.substring(newlineIndex + 2);

                    const eventTypeMatch = eventString.match(/^event: (.*)\n/);
                    const dataMatch = eventString.match(/\ndata: (.*)$/s);

                    if (eventTypeMatch && dataMatch) {
                        const eventType = eventTypeMatch[1];
                        const eventData = JSON.parse(dataMatch[1]);

                        if (eventType === 'log') {
                            liveLog.innerHTML += `<p>${eventData}</p>`;
                            liveLog.scrollTop = liveLog.scrollHeight;
                        } else if (eventType === 'partial_result') {
                            resultContent.innerHTML = eventData;
                        } else if (eventType === 'final_result') {
                            resultContent.innerHTML = eventData;
                        } else if (eventType === 'error') {
                            liveLog.innerHTML += `<p class="text-danger">Erro: ${eventData.error}</p>`;
                            resultContent.innerHTML = `<p class="text-danger">Ocorreu um erro: ${eventData.error}</p>`;
                            enableButtons();
                            reader.cancel(); // Cancela a leitura do stream em caso de erro
                            return;
                        } else if (eventType === 'end') {
                            enableButtons();
                            reader.cancel(); // Cancela a leitura do stream no final
                            return;
                        }
                    }
                }
            }
            enableButtons();

        } catch (error) {
            liveLog.innerHTML += `<p class="text-danger">${error.message}</p>`;
            resultContent.innerHTML = `<p class="text-danger">Ocorreu um erro. Tente novamente.</p>`;
            enableButtons();
        }
    };

    const clearResults = () => {
        liveLog.innerHTML = '';
        resultContent.innerHTML = '<div class="placeholder-glow"><span class="placeholder col-7"></span><span class="placeholder col-4"></span><span class="placeholder col-4"></span><span class="placeholder col-6"></span><span class="placeholder col-8"></span></div>';
    };

    const enableButtons = () => {
        const btnText = btnStep2.querySelector('.btn-text');
        const spinner = btnStep2.querySelector('.spinner-border');
        spinner.classList.add('d-none');
        btnStep2.disabled = false;
        btnText.textContent = 'Iniciar Sistema';
    };

    // Botão "Voltar ao Topo"
    window.addEventListener('scroll', () => {
        backToTopBtn.style.display = window.scrollY > 200 ? 'block' : 'none';
    });
    backToTopBtn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
});
