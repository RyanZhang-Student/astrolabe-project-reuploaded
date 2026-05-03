document.addEventListener('DOMContentLoaded', () => {
    window.starMythosData = null;
    fetch('star_mythos.json')
        .then(response => response.json())
        .then(data => { window.starMythosData = data; })
        .catch(err => console.error("Failed to load star mythos:", err));

    // Star Rendering & Modal Logic
    window.renderStarStats = function (stats) {
        const container = document.getElementById('star-conjunction-container');
        if (!container) return;

        const getStatSpan = (count, label, category, title) => {
            if (count > 0) {
                return `<span class="clickable-stat" onclick="window.openStarModal('${category}', '${title}')">${label}: ${count}</span>`;
            }
            return `<span>${label}: ${count}</span>`;
        };

        container.innerHTML = `
            <div class="stats-bar">
                ${getStatSpan(stats.royal, '👑 ROYAL STARS', 'is_royal', 'Royal Star Conjunctions')}
                ${getStatSpan(stats.behenian, '✨ BEHENIAN STARS', 'is_behenian', 'Behenian Star Conjunctions')}
                ${getStatSpan(stats.practical, '⚔️ PRACTICAL STARS', 'is_practical', 'Practical Star Conjunctions')}
                ${getStatSpan(stats.robson, '📚 ROBSON STARS', 'is_robson', 'Robson Star Conjunctions')}
            </div>
        `;
    };

    window.currentStarIndex = 0;
    window.currentStarData = [];

    window.openStarModal = function (category, title) {
        if (!window.starData || window.starData.length === 0) return;
        const modal = document.getElementById('starModal');
        const modalTitle = document.getElementById('modalTitle');

        modalTitle.innerText = "All Star Conjunctions";
        window.currentStarData = window.starData; // Show all

        window.renderStarList();
        window.backToStarList(); // Ensure we start at list view

        modal.classList.remove('hidden');
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    };

    window.renderStarList = function () {
        const listContainer = document.getElementById('starListView');
        listContainer.innerHTML = '';

        let tableHtml = `
            <table class="styled-star-table">
                <thead>
                    <tr>
                        <th style="text-align:left;">Star / Cusp head</th>
                        <th style="text-align:left;">Fixed star</th>
                        <th style="text-align:left;">Orb(°)</th>
                        <th style="text-align:left;">Meaning</th>
                    </tr>
                </thead>
                <tbody>
        `;

        window.starData.forEach((sa, index) => {
            let starNameClass = "";
            let prefix = "";
            let orbText = sa.orb.toFixed(2) + "&deg;";

            if (sa.is_royal) {
                starNameClass = "royal-star-text";
                prefix = "[王星] ";
            } else if (sa.is_behenian) {
                starNameClass = "behenian-star-text";
                prefix = "[Behenian] ";
            } else if (sa.is_practical) {
                starNameClass = "practical-star-text";
                prefix = "[实战] ";
            } else if (sa.is_robson) {
                starNameClass = "robson-star-text";
            }

            let meaningText = sa.meaning;
            if (!meaningText.startsWith("[")) {
                meaningText = prefix + meaningText;
            }

            tableHtml += `
                <tr onclick="window.showStarDetail(${index})">
                    <td class="planet-col">${sa.planet}</td>
                    <td class="star-col ${starNameClass}">${sa.star}</td>
                    <td class="orb-col">${orbText}</td>
                    <td class="meaning-col">${meaningText}</td>
                </tr>
            `;
        });

        tableHtml += `
                </tbody>
            </table>
        `;

        listContainer.innerHTML = tableHtml;
    };

    window.showStarDetail = function (index) {
        window.currentStarIndex = index;
        document.getElementById('starListView').classList.add('hidden');
        document.getElementById('starDetailView').classList.remove('hidden');
        window.renderSingleStar();
    };

    window.backToStarList = function () {
        document.getElementById('starListView').classList.remove('hidden');
        document.getElementById('starDetailView').classList.add('hidden');
    };

    window.renderSingleStar = function () {
        const content = document.getElementById('singleStarContent');
        const counter = document.getElementById('starCounter');
        const prevBtn = document.getElementById('prevStarBtn');
        const nextBtn = document.getElementById('nextStarBtn');

        const total = window.starData.length;
        const currentIndex = window.currentStarIndex;
        const sa = window.starData[currentIndex];

        counter.innerText = `${currentIndex + 1} / ${total}`;

        let detailHtml = `
            <div class="star-detail-row">
                <div class="star-detail-label">Planet & Star</div>
                <div class="star-detail-value">${sa.planet} &mdash; ${sa.star}</div>
            </div>
            <div class="star-detail-row">
                <div class="star-detail-label">Orb</div>
                <div class="star-detail-value orb-value">${sa.orb.toFixed(2)}&deg;</div>
            </div>
            <div class="star-detail-row">
                <div class="star-detail-label">Meaning</div>
                <div class="star-detail-value" style="font-size: 1rem; text-transform:none; line-height:1.6; text-align:left; padding: 0 1rem;">${sa.meaning}</div>
            </div>
        `;

        if (window.starMythosData) {
            let mythosObj = null;
            for (const key of Object.keys(window.starMythosData)) {
                if (key.includes(sa.star)) {
                    mythosObj = window.starMythosData[key];
                    break;
                }
            }

            if (mythosObj) {
                const addSection = (title, contentText) => {
                    if (!contentText) return '';
                    let formatted = contentText.replace(/\n/g, '<br/>');
                    return `
                        <div style="text-align: left; padding: 1.5rem 0 0 0; width:100%;">
                            <h4 style="color: #ffd700; margin-bottom: 0.75rem; font-size: 1.1rem; text-align:left;">${title}</h4>
                            <div style="color: var(--text-light); line-height: 1.6; font-size: 0.95rem;">${formatted}</div>
                        </div>
                    `;
                };

                // Add Deep Analysis styling container
                let mythosHtml = `<div style="margin-top: 1.5rem; padding-top: 0.5rem; border-top: 1px solid rgba(255, 255, 255, 0.1);">`;
                
                if (mythosObj.astrological_meaning && mythosObj.astrological_meaning.en) {
                    mythosHtml += addSection('Astrological Meaning', mythosObj.astrological_meaning.en);
                }
                if (mythosObj.deity && mythosObj.deity.en) {
                    mythosHtml += addSection('Representative Deity', mythosObj.deity.en);
                }
                if (mythosObj.origin && mythosObj.origin.en) {
                    mythosHtml += addSection('Origin', mythosObj.origin.en);
                }
                if (mythosObj.myth && mythosObj.myth.en) {
                    mythosHtml += addSection('Mythology', mythosObj.myth.en);
                }
                
                mythosHtml += `</div>`;
                detailHtml += mythosHtml;
            }
        }

        content.innerHTML = detailHtml;

        prevBtn.disabled = currentIndex === 0;
        nextBtn.disabled = currentIndex === total - 1;
    };

    window.nextStar = function () {
        if (window.currentStarIndex < window.starData.length - 1) {
            window.currentStarIndex++;
            window.renderSingleStar();
        }
    };

    window.prevStar = function () {
        if (window.currentStarIndex > 0) {
            window.currentStarIndex--;
            window.renderSingleStar();
        }
    };

    window.closeStarModal = function () {
        const modal = document.getElementById('starModal');
        modal.classList.add('hidden');
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    };

    window.addEventListener('click', (e) => {
        const modal = document.getElementById('starModal');
        if (e.target === modal) {
            window.closeStarModal();
        }
        
        const aiModal = document.getElementById('aiModal');
        if (e.target === aiModal) {
            window.closeAiModal();
        }
    });
});
