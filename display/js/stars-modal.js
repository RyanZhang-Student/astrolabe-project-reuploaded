document.addEventListener('DOMContentLoaded', () => {
    window.starMythosData = null;
    fetch('star_mythos.json')
        .then(response => response.json())
        .then(data => { window.starMythosData = data; })
        .catch(err => console.error("Failed to load star mythos:", err));

    // Star Rendering & Modal Logic
    window.renderStarStats = function (stats) {
        if (!stats) return;
        window.lastStarStats = stats;
        const container = document.getElementById('star-conjunction-container');
        if (!container) return;

        const lang = window.currentLanguage || 'en';
        const t = window.translations[lang] || window.translations['en'];

        const getStatSpan = (count, label, category, title) => {
            // Escape title string since it might have single quotes (like in French "d'Étoiles")
            const escapedTitle = title.replace(/'/g, "\\'");
            if (count > 0) {
                return `<span class="clickable-stat" onclick="window.openStarModal('${category}', '${escapedTitle}')">${label}: ${count}</span>`;
            }
            return `<span>${label}: ${count}</span>`;
        };

        container.innerHTML = `
            <div class="stats-bar">
                ${getStatSpan(stats.royal, t.label_royal_stars || '👑 ROYAL STARS', 'is_royal', t.title_royal_conjunctions || 'Royal Star Conjunctions')}
                ${getStatSpan(stats.behenian, t.label_behenian_stars || '✨ BEHENIAN STARS', 'is_behenian', t.title_behenian_conjunctions || 'Behenian Star Conjunctions')}
                ${getStatSpan(stats.practical, t.label_practical_stars || '⚔️ PRACTICAL STARS', 'is_practical', t.title_practical_conjunctions || 'Practical Star Conjunctions')}
                ${getStatSpan(stats.robson, t.label_robson_stars || '📚 ROBSON STARS', 'is_robson', t.title_robson_conjunctions || 'Robson Star Conjunctions')}
            </div>
        `;
    };

    window.currentStarIndex = 0;
    window.currentStarData = [];

    window.openStarModal = function (category, title) {
        if (!window.starData || window.starData.length === 0) return;
        const modal = document.getElementById('starModal');
        const modalTitle = document.getElementById('modalTitle');

        const lang = window.currentLanguage || 'en';
        const t = window.translations[lang] || window.translations['en'];
        modalTitle.innerText = t.star_modal_title || "All Star Conjunctions";
        
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

        const lang = window.currentLanguage || 'en';
        const t = window.translations[lang] || window.translations['en'];

        const getPlanetName = (planetEn, l) => {
            if (l === 'en') return planetEn;
            const zhMap = {
                'Sun': '太阳', 'Moon': '月亮', 'Mercury': '水星', 'Venus': '金星', 'Mars': '火星',
                'Jupiter': '木星', 'Saturn': '土星', 'Uranus': '天王星', 'Neptune': '海王星', 'Pluto': '冥王星',
                'Ascendant': '上升点', 'Midheaven': '中天', 'Descendant': '下降点', 'IC': '天底',
                'North Node': '北交点', 'South Node': '南交点', 'Chiron': '凯龙星', 'Lilith': '暗月莉莉丝',
                'Part of Fortune': '福点'
            };
            const frMap = {
                'Sun': 'Soleil', 'Moon': 'Lune', 'Mercury': 'Mercure', 'Venus': 'Vénus', 'Mars': 'Mars',
                'Jupiter': 'Jupiter', 'Saturn': 'Saturne', 'Uranus': 'Uranus', 'Neptune': 'Neptune', 'Pluto': 'Pluton',
                'Ascendant': 'Ascendant', 'Midheaven': 'Milieu du Ciel', 'Descendant': 'Descendant', 'IC': 'Fond du Ciel',
                'North Node': 'Nœud Nord', 'South Node': 'Nœud Sud', 'Chiron': 'Chiron', 'Lilith': 'Lune Noire',
                'Part of Fortune': 'Part de Fortune'
            };
            const esMap = {
                'Sun': 'Sol', 'Moon': 'Luna', 'Mercury': 'Mercurio', 'Venus': 'Venus', 'Mars': 'Marte',
                'Jupiter': 'Júpiter', 'Saturn': 'Saturno', 'Uranus': 'Urano', 'Neptune': 'Neptuno', 'Pluto': 'Plutón',
                'Ascendant': 'Ascendente', 'Midheaven': 'Medio Cielo', 'Descendant': 'Descendente', 'IC': 'Fondo del Cielo',
                'North Node': 'Nodo Norte', 'South Node': 'Nodo Sur', 'Chiron': 'Quirón', 'Lilith': 'Lilith',
                'Part of Fortune': 'Parte de la Fortuna'
            };
            let name = planetEn;
            if (l === 'zh' && zhMap[planetEn]) name = zhMap[planetEn];
            if (l === 'fr' && frMap[planetEn]) name = frMap[planetEn];
            if (l === 'es' && esMap[planetEn]) name = esMap[planetEn];
            const match = name.match(/House (\d+) cusp head/i);
            if (match) {
                if (l === 'zh') return `第 ${match[1]} 宫宫头`;
                if (l === 'fr') return `Cuspide Maison ${match[1]}`;
                if (l === 'es') return `Cúspide de la Casa ${match[1]}`;
            }
            return name;
        };

        let tableHtml = `
            <table class="styled-star-table">
                <thead>
                    <tr>
                        <th style="text-align:left;">${t.star_col_cusp || 'Star / Cusp head'}</th>
                        <th style="text-align:left;">${t.star_col_fixed || 'Fixed star'}</th>
                        <th style="text-align:left;">${t.star_col_orb || 'Orb(°)'}</th>
                        <th style="text-align:left;">${t.star_col_meaning || 'Meaning'}</th>
                    </tr>
                </thead>
                <tbody>
        `;

        window.starData.forEach((sa, index) => {
            let starNameClass = "";
            let prefix = "";
            let orbText = sa.orb.toFixed(2) + "&deg;";

            // Look up mythos object for translation
            let mythosObj = null;
            if (window.starMythosData) {
                for (const key of Object.keys(window.starMythosData)) {
                    if (key.includes(sa.star)) {
                        mythosObj = window.starMythosData[key];
                        break;
                    }
                }
            }

            let mythosLang = lang === 'zh' ? 'cn' : lang;

            if (sa.is_royal) {
                starNameClass = "royal-star-text";
                prefix = lang === 'fr' ? "[Étoile Royale] " : (lang === 'es' ? "[Estrella Real] " : (lang === 'zh' ? "[王室恒星] " : "[Royal Star] "));
            } else if (sa.is_behenian) {
                starNameClass = "behenian-star-text";
                prefix = lang === 'zh' ? "[比黑尼星] " : (lang === 'es' ? "[Estrella Beheniana] " : "[Behenian] ");
            } else if (sa.is_practical) {
                starNameClass = "practical-star-text";
                prefix = lang === 'fr' ? "[Pratique] " : (lang === 'es' ? "[Práctica] " : (lang === 'zh' ? "[实用恒星] " : "[Practical] "));
            } else if (sa.is_robson) {
                starNameClass = "robson-star-text";
                prefix = lang === 'zh' ? "[罗伯逊星] " : (lang === 'es' ? "[Estrella Robson] " : "");
            }

            let meaningText = sa.meaning;
            if (mythosObj && mythosObj.astrological_meaning) {
                meaningText = mythosObj.astrological_meaning[mythosLang] || mythosObj.astrological_meaning['en'] || sa.meaning;
            }

            if (!meaningText.startsWith("[")) {
                meaningText = prefix + meaningText;
            }

            let displayStar = sa.star;
            if (lang === 'zh' && window.starMythosData) {
                for (const key of Object.keys(window.starMythosData)) {
                    if (key.includes(sa.star)) {
                        const cnMatch = key.match(/\((.*?)\)/);
                        if (cnMatch) displayStar = `${sa.star} <span style="font-size:0.85em; opacity:0.8;">${cnMatch[0]}</span>`;
                        break;
                    }
                }
            }

            let displayPlanet = getPlanetName(sa.planet, lang);

            tableHtml += `
                <tr onclick="window.showStarDetail(${index})">
                    <td class="planet-col">${displayPlanet}</td>
                    <td class="star-col ${starNameClass}">${displayStar}</td>
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
        document.getElementById('starModal').classList.add('detail-active');
        document.getElementById('starListView').classList.add('hidden');
        document.getElementById('starDetailView').classList.remove('hidden');
        window.renderSingleStar();
    };

    window.backToStarList = function () {
        document.getElementById('starModal').classList.remove('detail-active');
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

        const lang = window.currentLanguage || 'en';
        const t = window.translations[lang] || window.translations['en'];

        // Find mythosObj
        let mythosObj = null;
        if (window.starMythosData) {
            for (const key of Object.keys(window.starMythosData)) {
                if (key.includes(sa.star)) {
                    mythosObj = window.starMythosData[key];
                    break;
                }
            }
        }

        const getPlanetName = (planetEn, l) => {
            if (l === 'en') return planetEn;
            const zhMap = {
                'Sun': '太阳', 'Moon': '月亮', 'Mercury': '水星', 'Venus': '金星', 'Mars': '火星',
                'Jupiter': '木星', 'Saturn': '土星', 'Uranus': '天王星', 'Neptune': '海王星', 'Pluto': '冥王星',
                'Ascendant': '上升点', 'Midheaven': '中天', 'Descendant': '下降点', 'IC': '天底',
                'North Node': '北交点', 'South Node': '南交点', 'Chiron': '凯龙星', 'Lilith': '暗月莉莉丝',
                'Part of Fortune': '福点'
            };
            const frMap = {
                'Sun': 'Soleil', 'Moon': 'Lune', 'Mercury': 'Mercure', 'Venus': 'Vénus', 'Mars': 'Mars',
                'Jupiter': 'Jupiter', 'Saturn': 'Saturne', 'Uranus': 'Uranus', 'Neptune': 'Neptune', 'Pluto': 'Pluton',
                'Ascendant': 'Ascendant', 'Midheaven': 'Milieu du Ciel', 'Descendant': 'Descendant', 'IC': 'Fond du Ciel',
                'North Node': 'Nœud Nord', 'South Node': 'Nœud Sud', 'Chiron': 'Chiron', 'Lilith': 'Lune Noire',
                'Part of Fortune': 'Part de Fortune'
            };
            const esMap = {
                'Sun': 'Sol', 'Moon': 'Luna', 'Mercury': 'Mercurio', 'Venus': 'Venus', 'Mars': 'Marte',
                'Jupiter': 'Júpiter', 'Saturn': 'Saturno', 'Uranus': 'Urano', 'Neptune': 'Neptuno', 'Pluto': 'Plutón',
                'Ascendant': 'Ascendente', 'Midheaven': 'Medio Cielo', 'Descendant': 'Descendente', 'IC': 'Fondo del Cielo',
                'North Node': 'Nodo Norte', 'South Node': 'Nodo Sur', 'Chiron': 'Quirón', 'Lilith': 'Lilith',
                'Part of Fortune': 'Parte de la Fortuna'
            };
            let name = planetEn;
            if (l === 'zh' && zhMap[planetEn]) name = zhMap[planetEn];
            if (l === 'fr' && frMap[planetEn]) name = frMap[planetEn];
            if (l === 'es' && esMap[planetEn]) name = esMap[planetEn];
            const match = name.match(/House (\d+) cusp head/i);
            if (match) {
                if (l === 'zh') return `第 ${match[1]} 宫宫头`;
                if (l === 'fr') return `Cuspide Maison ${match[1]}`;
                if (l === 'es') return `Cúspide de la Casa ${match[1]}`;
            }
            return name;
        };

        let mythosLang = lang === 'zh' ? 'cn' : lang;
        let meaningText = sa.meaning;
        if (mythosObj && mythosObj.astrological_meaning) {
            meaningText = mythosObj.astrological_meaning[mythosLang] || mythosObj.astrological_meaning['en'] || sa.meaning;
        }

        let displayPlanet = getPlanetName(sa.planet, lang);
        
        let displayStar = sa.star;
        if (lang === 'zh' && window.starMythosData) {
            for (const key of Object.keys(window.starMythosData)) {
                if (key.includes(sa.star)) {
                    const cnMatch = key.match(/\((.*?)\)/);
                    if (cnMatch) displayStar = `${sa.star} ${cnMatch[0]}`;
                    break;
                }
            }
        }

        let detailHtml = `
            <div class="star-detail-row">
                <div class="star-detail-label">${t.star_label_planet_star || 'Planet & Star'}</div>
                <div class="star-detail-value">${displayPlanet} &mdash; ${displayStar}</div>
            </div>
            <div class="star-detail-row">
                <div class="star-detail-label">${t.star_label_orb || 'Orb'}</div>
                <div class="star-detail-value orb-value">${sa.orb.toFixed(2)}&deg;</div>
            </div>
            <div class="star-detail-row">
                <div class="star-detail-label">${t.star_label_meaning || 'Meaning'}</div>
                <div class="star-detail-value" style="font-size: 1rem; text-transform:none; line-height:1.6; text-align:left; padding: 0 1rem;">${meaningText}</div>
            </div>
        `;

        if (mythosObj) {
            const getLangField = (field) => {
                if (!field) return '';
                let mythosLang = lang === 'zh' ? 'cn' : lang;
                return field[mythosLang] || field['en'] || '';
            };

            const addSection = (titleKey, defaultTitle, field) => {
                const textVal = getLangField(field);
                if (!textVal) return '';
                let formatted = textVal.replace(/\n/g, '<br/>');
                const title = t[titleKey] || defaultTitle;
                return `
                    <div style="text-align: left; padding: 1.5rem 0 0 0; width:100%;">
                        <h4 style="color: #ffd700; margin-bottom: 0.75rem; font-size: 1.1rem; text-align:left;">${title}</h4>
                        <div style="color: var(--text-light); line-height: 1.6; font-size: 0.95rem;">${formatted}</div>
                    </div>
                `;
            };

            // Add Deep Analysis styling container
            let mythosHtml = `<div style="margin-top: 1.5rem; padding-top: 0.5rem; border-top: 1px solid rgba(255, 255, 255, 0.1);">`;
            
            mythosHtml += addSection('star_label_astrological_meaning', 'Astrological Meaning', mythosObj.astrology_meaning);
            mythosHtml += addSection('star_label_deity', 'Representative Deity', mythosObj.deity);
            mythosHtml += addSection('star_label_origin', 'Origin', mythosObj.origin);
            mythosHtml += addSection('star_label_mythology', 'Mythology', mythosObj.myth);
            
            mythosHtml += `</div>`;
            detailHtml += mythosHtml;
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
