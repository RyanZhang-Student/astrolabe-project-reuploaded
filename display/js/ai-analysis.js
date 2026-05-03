document.addEventListener('DOMContentLoaded', () => {
    // AI Analysis Logic
    let selectedHouse = null;
    const houseBlocks = document.querySelectorAll('.house-block');
    const aiAnalyzeBtn = document.getElementById('ai-analyze-btn');
    const aiBtnText = aiAnalyzeBtn.querySelector('.ai-btn-text');
    const aiLoader = document.getElementById('ai-loader');

    houseBlocks.forEach(block => {
        block.addEventListener('click', () => {
            houseBlocks.forEach(b => b.classList.remove('selected'));
            block.classList.add('selected');
            selectedHouse = block.dataset.house;
            
            aiAnalyzeBtn.classList.remove('disabled');
            aiAnalyzeBtn.disabled = false;
        });
    });

    aiAnalyzeBtn.addEventListener('click', async () => {
        if (!selectedHouse || aiAnalyzeBtn.classList.contains('disabled')) return;
        
        const userName = window.currentAnalysisUserName;
        if (!userName) {
            alert('User name not found. Please re-calculate the chart.');
            return;
        }

        // Show loading state
        aiBtnText.style.opacity = '0';
        aiLoader.style.display = 'block';
        aiAnalyzeBtn.disabled = true;

        try {
            const response = await fetch('/api/ai_analysis', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_name: userName,
                    house_number: parseInt(selectedHouse)
                })
            });

            const result = await response.json();
            
            aiBtnText.style.opacity = '1';
            aiLoader.style.display = 'none';
            aiAnalyzeBtn.disabled = false;

            if (response.ok && result.status === 'success') {
                showAiModal(result.analysis, selectedHouse);
            } else {
                alert('Analysis failed: ' + (result.error || 'Unknown error'));
            }
        } catch (error) {
            console.error('AI Fetch error:', error);
            alert('An error occurred while fetching AI analysis.');
            aiBtnText.style.opacity = '1';
            aiLoader.style.display = 'none';
            aiAnalyzeBtn.disabled = false;
        }
    });

    function showAiModal(markdownText, house) {
        document.getElementById('aiModalTitle').innerText = `AI House ${house} Interpretation`;
        
        // Very basic simple markdown parser for the gemini response
        let htmlText = markdownText
            .replace(/### (.*)/g, '<h3>$1</h3>')
            .replace(/## (.*)/g, '<h2>$1</h2>')
            .replace(/# (.*)/g, '<h1>$1</h1>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br/>');
            
        // Check for lists
        htmlText = htmlText.replace(/<br\/>- /g, '<li>').replace(/<p>- /g, '<p><li>');
            
        htmlText = `<p>${htmlText}</p>`;
        
        document.getElementById('aiResultContent').innerHTML = htmlText;
        
        const aiModal = document.getElementById('aiModal');
        aiModal.classList.remove('hidden');
        aiModal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }

    window.closeAiModal = function() {
        const aiModal = document.getElementById('aiModal');
        aiModal.classList.add('hidden');
        aiModal.style.display = 'none';
        document.body.style.overflow = 'auto';
    };

});
