document.addEventListener('DOMContentLoaded', () => {
    createStars();
    window.timePicker.init();
    
    // --- Language Logic ---
    window.planetAbbreviations = {
        'en': {
            'Sun': 'Su', 'Moon': 'Mo', 'Mercury': 'Me', 'Venus': 'Ve',
            'Mars': 'Ma', 'Jupiter': 'Ju', 'Saturn': 'Sa', 'Uranus': 'Ur',
            'Neptune': 'Ne', 'Pluto': 'Pl', 'North Node': 'No', 'South Node': 'So',
            'Fortune': 'Fo'
        },
        'fr': {
            'Sun': 'Sol', 'Moon': 'Lun', 'Mercury': 'Mer', 'Venus': 'Ven',
            'Mars': 'Mar', 'Jupiter': 'Jup', 'Saturn': 'Sat', 'Uranus': 'Ura',
            'Neptune': 'Nep', 'Pluto': 'Plu', 'North Node': 'NdN', 'South Node': 'NdS',
            'Fortune': 'PdF'
        }
    };

    window.signAbbreviations = {
        'en': {
            'Aries': 'Ari', 'Taurus': 'Tau', 'Gemini': 'Gem', 'Cancer': 'Can',
            'Leo': 'Leo', 'Virgo': 'Vir', 'Libra': 'Lib', 'Scorpio': 'Sco',
            'Sagittarius': 'Sag', 'Capricorn': 'Cap', 'Aquarius': 'Aqu', 'Pisces': 'Pis'
        },
        'fr': {
            'Aries': 'Bél', 'Taurus': 'Tau', 'Gemini': 'Gém', 'Cancer': 'Can',
            'Leo': 'Lio', 'Virgo': 'Vie', 'Libra': 'Bal', 'Scorpio': 'Sco',
            'Sagittarius': 'Sag', 'Capricorn': 'Cap', 'Aquarius': 'Ver', 'Pisces': 'Poi'
        }
    };

    window.pointAbbreviations = {
        'en': {
            'ASC': 'ASC', 'DES': 'DES', 'MC': 'MC', 'IC': 'IC', 'As': 'As', 'Mi': 'Mi'
        },
        'fr': {
            'ASC': 'ASC', 'DES': 'DES', 'MC': 'MC', 'IC': 'FC', 'As': 'As', 'Mi': 'Mi'
        }
    };

    window.renderLocalizedChart = function(lang) {
        if (!window.originalChartSvgBase64) return;
        
        const abbrDict = window.planetAbbreviations[lang] || window.planetAbbreviations['en'];
        const signDict = window.signAbbreviations[lang] || window.signAbbreviations['en'];
        const pointDict = window.pointAbbreviations[lang] || window.pointAbbreviations['en'];
        
        let svgStr = decodeURIComponent(escape(atob(window.originalChartSvgBase64)));
        
        svgStr = svgStr.replace(/<text\s+data-planet="([^"]+)"([^>]*)>([^<]*)<\/text>/g, (match, planetName, restOfTag, oldAbbr) => {
            const newAbbr = abbrDict[planetName] || oldAbbr;
            return `<text data-planet="${planetName}"${restOfTag}>${newAbbr}</text>`;
        });

        svgStr = svgStr.replace(/<text\s+data-sign="([^"]+)"([^>]*)>([^<]*)<\/text>/g, (match, signName, restOfTag, oldAbbr) => {
            const newAbbr = signDict[signName] || oldAbbr;
            return `<text data-sign="${signName}"${restOfTag}>${newAbbr}</text>`;
        });

        svgStr = svgStr.replace(/<text\s+data-point="([^"]+)"([^>]*)>([^<]*)<\/text>/g, (match, pointName, restOfTag, oldAbbr) => {
            const newAbbr = pointDict[pointName] || oldAbbr;
            return `<text data-point="${pointName}"${restOfTag}>${newAbbr}</text>`;
        });
        
        const newBase64 = btoa(unescape(encodeURIComponent(svgStr)));
        
        const img = new Image();
        img.onload = function () {
            const canvas = document.createElement('canvas');
            canvas.width = 800;
            canvas.height = 800;
            const ctx = canvas.getContext('2d');

            ctx.fillStyle = '#0d0b14';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

            const ptrUrl = canvas.toDataURL('image/png');
            const chartImg = document.getElementById('natal-chart-img');
            if (chartImg) {
                chartImg.src = ptrUrl;
                const container = document.getElementById('chart-image-container');
                if (container) container.classList.remove('hidden');
            }
        };
        img.src = 'data:image/svg+xml;base64,' + newBase64;
    };

    window.currentLanguage = localStorage.getItem('language') || 'en';
    
    window.updatePageLanguage = function(lang) {
        window.currentLanguage = lang;
        localStorage.setItem('language', lang);
        const dict = window.translations[lang];
        if (!dict) return;
        
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            if (dict[key]) el.textContent = dict[key];
        });
        document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
            const key = el.getAttribute('data-i18n-placeholder');
            if (dict[key]) el.placeholder = dict[key];
        });
        
        const langBtn = document.getElementById('lang-btn');
        if (langBtn) langBtn.textContent = lang.toUpperCase();

        // Dynamically update star modal contents if it is open
        const starModal = document.getElementById('starModal');
        if (starModal && !starModal.classList.contains('hidden')) {
            const modalTitle = document.getElementById('modalTitle');
            if (modalTitle) {
                modalTitle.innerText = dict.star_modal_title || "All Star Conjunctions";
            }
            if (typeof window.renderStarList === 'function') {
                window.renderStarList();
            }
            if (starModal.classList.contains('detail-active') && typeof window.renderSingleStar === 'function') {
                window.renderSingleStar();
            }
        }

        // Dynamically update the star stats bar if we have previously generated stats
        if (window.lastStarStats && typeof window.renderStarStats === 'function') {
            window.renderStarStats(window.lastStarStats);
        }

        if (typeof window.renderLocalizedChart === 'function') {
            window.renderLocalizedChart(lang);
        }
    };
    
    window.updatePageLanguage(window.currentLanguage);
    
    const langBtn = document.getElementById('lang-btn');
    const langDropdown = document.getElementById('lang-dropdown');
    if (langBtn && langDropdown) {
        langBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            langDropdown.classList.toggle('hidden');
        });
        document.addEventListener('click', (e) => {
            if (!langDropdown.contains(e.target) && e.target !== langBtn) {
                langDropdown.classList.add('hidden');
            }
        });
        document.querySelectorAll('.lang-option').forEach(btn => {
            btn.addEventListener('click', () => {
                window.updatePageLanguage(btn.getAttribute('data-lang'));
                langDropdown.classList.add('hidden');
            });
        });
    }
    // --- End Language Logic ---

    const form = document.getElementById('astrolabe-form');
    const submitBtn = document.getElementById('submit-btn');
    const btnText = submitBtn.querySelector('.btn-text');
    const loader = document.getElementById('loader');
    const resultContainer = document.getElementById('result-container');
    const reportLink = document.getElementById('report-link');

    // Gender selection logic
    const genderBoxes = document.querySelectorAll('.gender-box');
    const genderInput = document.getElementById('gender');

    const formSection = document.getElementById('form-section');
    const summaryPillContainer = document.getElementById('summary-pill-container');
    const summaryPillText = document.getElementById('summary-pill-text');
    const summaryPill = document.getElementById('summary-pill');

    const showSummaryPill = (state) => {
        const name = state.name || 'User';
        let displayTime = '';
        if (state.date && state.time) {
            displayTime = `${state.date} ${state.time}:00`;
        }
        if (summaryPillText) {
            summaryPillText.textContent = `${name}: ${displayTime}`;
        }
        if (formSection && summaryPillContainer) {
            formSection.classList.add('hidden');
            summaryPillContainer.classList.remove('hidden');
        }
    };

    if (summaryPill) {
        summaryPill.addEventListener('click', () => {
            summaryPillContainer.classList.add('hidden');
            if (formSection) formSection.classList.remove('hidden');
            if (resultContainer) resultContainer.classList.add('hidden');
        });
    }

    const menuEditInfoBtn = document.getElementById('menu-edit-info-btn');
    if (menuEditInfoBtn) {
        menuEditInfoBtn.addEventListener('click', () => {
            if (summaryPillContainer) summaryPillContainer.classList.add('hidden');
            if (formSection) formSection.classList.remove('hidden');
            if (resultContainer) resultContainer.classList.add('hidden');

            const profilePopup = document.getElementById('profile-popup');
            const profileOverlay = document.getElementById('profile-overlay');
            if (profilePopup) profilePopup.classList.add('hidden');
            if (profileOverlay) profileOverlay.classList.remove('active');
        });
    }

    window.saveFormState = (autoSubmit = false) => {
        const state = {
            name: document.getElementById('name').value,
            gender: genderInput.value,
            location: document.getElementById('location').value,
            date: document.getElementById('birth-date').value,
            time: document.getElementById('birth-time').value,
            autoSubmit: autoSubmit
        };
        localStorage.setItem('astrolabeFormState', JSON.stringify(state));
    };

    const restoreFormState = () => {
        const saved = localStorage.getItem('astrolabeFormState');
        if (saved) {
            try {
                const state = JSON.parse(saved);
                window.lastSubmittedState = JSON.parse(saved); // Store the actual submitted state for comparison
                if (state.name) document.getElementById('name').value = state.name;
                if (state.gender) {
                    genderInput.value = state.gender;
                    genderBoxes.forEach(b => {
                        if (b.dataset.value === state.gender) {
                            b.classList.add('selected');
                            b.parentElement.classList.add('gender-selected');
                        }
                    });
                }
                if (state.location) document.getElementById('location').value = state.location;
                if (state.date) document.getElementById('birth-date').value = state.date;
                if (state.time) document.getElementById('birth-time').value = state.time;

                const isLoggedIn = document.getElementById('login-btn') === null;
                const isFullyPopulated = state.name && state.date && state.time;

                if (state.autoSubmit && isLoggedIn) {
                    state.autoSubmit = false;
                    localStorage.setItem('astrolabeFormState', JSON.stringify(state));
                    setTimeout(() => {
                        const submitBtn = document.getElementById('submit-btn');
                        if (submitBtn) submitBtn.click();
                    }, 500);
                } else if (isFullyPopulated) {
                    showSummaryPill(state);
                    if (isLoggedIn) {
                        setTimeout(() => {
                            const submitBtn = document.getElementById('submit-btn');
                            if (submitBtn) submitBtn.click();
                        }, 500);
                    }
                }
            } catch (e) {
                console.error("Error restoring form state", e);
            }
        }
    };

    genderBoxes.forEach(box => {
        box.addEventListener('click', () => {
            // Remove selected class from all
            genderBoxes.forEach(b => b.classList.remove('selected'));
            // Add selected class to correct one
            box.classList.add('selected');
            // Set hidden input value
            genderInput.value = box.dataset.value;
            // Add class to container to enable post-selection hover styles
            box.parentElement.classList.add('gender-selected');
            window.saveFormState(false);
        });
    });

    const locationInput = document.getElementById('location');
    const autocompleteList = document.getElementById('autocomplete-list');

    // Restore state on load
    restoreFormState();

    const countryMap = {
        'CN': 'CHINA', 'US': 'UNITED STATES', 'GB': 'UNITED KINGDOM',
        'CA': 'CANADA', 'AU': 'AUSTRALIA', 'DE': 'GERMANY', 'FR': 'FRANCE', 'JP': 'JAPAN',
        'IN': 'INDIA', 'BR': 'BRAZIL', 'RU': 'RUSSIA', 'KR': 'SOUTH KOREA',
        'IT': 'ITALY', 'ES': 'SPAIN', 'MX': 'MEXICO', 'VN': 'VIETNAM', 'TH': 'THAILAND'
    };

    const getCountryName = (code) => {
        try {
            const regionNames = new Intl.DisplayNames(['en'], { type: 'region' });
            return regionNames.of(code).toUpperCase();
        } catch (e) {
            return countryMap[code] || code;
        }
    };

    let debounceTimeout = null;

    locationInput.addEventListener('input', function () {
        const val = this.value;
        if (!val) {
            autocompleteList.classList.add('hidden');
            return;
        }

        clearTimeout(debounceTimeout);
        debounceTimeout = setTimeout(async () => {
            try {
                const response = await fetch(`/api/cities?q=${encodeURIComponent(val)}`);
                const matches = await response.json();

                if (!matches || matches.length === 0) {
                    autocompleteList.classList.add('hidden');
                    return;
                }

                autocompleteList.innerHTML = '';
                matches.forEach(item => {
                    const div = document.createElement('div');
                    div.className = 'autocomplete-item';
                    const countryName = getCountryName(item.country);
                    div.innerHTML = `<strong>${item.name}</strong> - ${countryName}`;

                    div.addEventListener('click', function (e) {
                        locationInput.value = `${item.name}-${countryName}`;
                        autocompleteList.classList.add('hidden');
                    });

                    autocompleteList.appendChild(div);
                });

                autocompleteList.classList.remove('hidden');
            } catch (err) {
                console.error("Autocomplete fetch error: ", err);
            }
        }, 300);
    });

    // Close dropdown on click outside
    document.addEventListener('click', function (e) {
        if (e.target !== locationInput) {
            autocompleteList.classList.add('hidden');
        }
    });

    // Handle form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Check if user is logged in
        const loginBtn = document.getElementById('login-btn');
        if (loginBtn) {
            // Show registration modal instead of direct login trigger
            window.saveFormState(true);
            const regModal = document.getElementById('reg-modal');
            if (regModal) {
                regModal.classList.remove('hidden');
            }
            return; // Stop execution, wait for user action
        }

        if (!genderInput.value) {
            alert('Please select a gender.');
            return;
        }

        let isChanged = true;
        if (window.lastSubmittedState) {
            const savedState = window.lastSubmittedState;
            const currentName = document.getElementById('name').value;
            const currentGender = genderInput.value;
            const currentLocation = document.getElementById('location').value;
            const currentDate = document.getElementById('birth-date').value;
            const currentTime = document.getElementById('birth-time').value;
            
            if (savedState.name === currentName &&
                savedState.gender === currentGender &&
                savedState.location === currentLocation &&
                savedState.date === currentDate &&
                savedState.time === currentTime) {
                isChanged = false;
            }
        }

        if (e.isTrusted && window.lastSubmittedState && isChanged && !window.skipConfirmModal) {
            const confirmModal = document.getElementById('update-confirm-modal');
            if (confirmModal) {
                confirmModal.classList.remove('hidden');
                return; // Stop here, wait for confirmation
            }
        }
        window.skipConfirmModal = false;

        // UI Feedback
        btnText.style.opacity = '0';
        loader.style.display = 'block';
        submitBtn.disabled = true;
        resultContainer.classList.add('hidden');

        // Collect Data
        const name = document.getElementById('name').value;
        const gender = genderInput.value;
        const location = document.getElementById('location').value;
        const dateRaw = document.getElementById('birth-date').value; // YYYY-MM-DD
        const timeRaw = document.getElementById('birth-time').value; // HH:MM

        // Format to YYYY-MMDD-HHMM
        const [year, month, day] = dateRaw.split('-');
        const [hour, minute] = timeRaw.split(':');
        const dobFormatted = `${year}-${month}${day}-${hour}${minute}`;

        try {
            const response = await fetch('/calculate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: name,
                    gender: gender,
                    location: location,
                    dob: dobFormatted,
                    lang: window.currentLanguage
                })
            });

            const result = await response.json();

            if (response.ok) {
                btnText.style.opacity = '1';
                loader.style.display = 'none';
                submitBtn.disabled = false;

                const currentState = {
                    name: document.getElementById('name').value,
                    gender: genderInput.value,
                    location: document.getElementById('location').value,
                    date: document.getElementById('birth-date').value,
                    time: document.getElementById('birth-time').value,
                    autoSubmit: false
                };
                showSummaryPill(currentState);
                localStorage.setItem('astrolabeFormState', JSON.stringify(currentState));
                window.lastSubmittedState = JSON.parse(JSON.stringify(currentState));

                resultContainer.classList.remove('hidden');
                reportLink.textContent = `View Report for ${name}`;
                reportLink.href = result.report_url || `/results/report_${name.toUpperCase()}.html`;

                // Render Chart Photo via Canvas to ensure it is a raster image, not decipherable HTML/SVG
                if (result.chart_svg_base64) {
                    window.originalChartSvgBase64 = result.chart_svg_base64;
                    window.renderLocalizedChart(window.currentLanguage);
                }

                // Render Star Conjunctions
                if (result.star_stats) {
                    window.starData = result.star_aspects || [];
                    window.renderStarStats(result.star_stats);
                }

                // Show AI Analysis section and store current user
                window.currentAnalysisUserName = result.user_name || name;
                document.getElementById('ai-analysis-container').classList.remove('hidden');
                document.getElementById('consult-section').classList.remove('hidden');

            } else {
                alert('Error: ' + (result.error || 'Failed to calculate'));
                btnText.style.opacity = '1';
                loader.style.display = 'none';
                submitBtn.disabled = false;
            }
        } catch (error) {
            console.error('Fetch error:', error);
            alert('An error occurred during calculation.');
            btnText.style.opacity = '1';
            loader.style.display = 'none';
            submitBtn.disabled = false;
        }
    });

    // Registration Modal event listeners
    const modalLoginBtn = document.getElementById('modal-login-btn');
    const modalCloseBtn = document.getElementById('modal-close-btn');
    const regModal = document.getElementById('reg-modal');

    if (modalLoginBtn && modalCloseBtn && regModal) {
        modalCloseBtn.addEventListener('click', () => {
            regModal.classList.add('hidden');
        });

        modalLoginBtn.addEventListener('click', () => {
            const loginBtn = document.getElementById('login-btn');
            if (loginBtn) {
                loginBtn.click();
            }
        });

        regModal.addEventListener('click', (e) => {
            if (e.target === regModal) {
                regModal.classList.add('hidden');
            }
        });
    }

    // Confirm Update Modal event listeners
    const confirmUpdateModal = document.getElementById('update-confirm-modal');
    const confirmUpdateYes = document.getElementById('confirm-update-yes');
    const confirmUpdateNo = document.getElementById('confirm-update-no');

    if (confirmUpdateModal && confirmUpdateYes && confirmUpdateNo) {
        confirmUpdateYes.addEventListener('click', () => {
            confirmUpdateModal.classList.add('hidden');
            window.skipConfirmModal = true;
            const submitBtn = document.getElementById('submit-btn');
            if (submitBtn) submitBtn.click();
        });
        
        const closeConfirmModal = () => {
            confirmUpdateModal.classList.add('hidden');
            if (window.lastSubmittedState) {
                showSummaryPill(window.lastSubmittedState);
                const resultContainer = document.getElementById('result-container');
                if (resultContainer) resultContainer.classList.remove('hidden');
            }
        };

        confirmUpdateNo.addEventListener('click', closeConfirmModal);
        
        confirmUpdateModal.addEventListener('click', (e) => {
            if (e.target === confirmUpdateModal) {
                closeConfirmModal();
            }
        });
    }

    // View Full Analysis Report Generation
    const viewFullReportBtn = document.getElementById('view-full-report-btn');
    if (viewFullReportBtn) {
        viewFullReportBtn.addEventListener('click', async () => {
            viewFullReportBtn.disabled = true;
            const originalText = viewFullReportBtn.innerHTML;
            viewFullReportBtn.innerHTML = '<span class="btn-icon">⏳</span><span class="btn-text">Generating Report...</span>';

            // Open a new tab immediately to bypass popup blockers
            const reportWindow = window.open('', '_blank');
            if (reportWindow) {
                reportWindow.document.write(`
                    <html>
                    <head>
                        <title>Generating Astrological Report...</title>
                        <style>
                            body {
                                background-color: #0d0b14;
                                color: #e6c98b;
                                font-family: 'Inter', sans-serif;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                height: 100vh;
                                margin: 0;
                                text-align: center;
                            }
                            .loader {
                                border: 4px solid rgba(230, 201, 139, 0.1);
                                border-top: 4px solid #ffcc00;
                                border-radius: 50%;
                                width: 50px;
                                height: 50px;
                                animation: spin 1s linear infinite;
                                margin: 0 auto 24px;
                                box-shadow: 0 0 15px rgba(255, 204, 0, 0.2);
                            }
                            h2 {
                                font-weight: 300;
                                letter-spacing: 2px;
                                margin-bottom: 8px;
                            }
                            p {
                                color: #a0aec0;
                                font-size: 0.95rem;
                            }
                            @keyframes spin {
                                0% { transform: rotate(0deg); }
                                100% { transform: rotate(360deg); }
                            }
                        </style>
                    </head>
                    <body>
                        <div>
                            <div class="loader"></div>
                            <h2>ASTROLABE</h2>
                            <p>Analyzing Natal Chart and Generating Premium Report...</p>
                        </div>
                    </body>
                    </html>
                `);
                reportWindow.document.close();
            }

            try {
                const chartImgEl = document.getElementById('natal-chart-img');
                const chartImgBase64 = chartImgEl ? chartImgEl.src : '';
                const nameVal = document.getElementById('name').value;
                const birthDateVal = document.getElementById('birth-date').value;
                const birthTimeVal = document.getElementById('birth-time').value;
                const locationVal = document.getElementById('location').value;

                const response = await fetch('/generate_pdf', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        chart_img: chartImgBase64,
                        name: nameVal,
                        birth_date: birthDateVal,
                        birth_time: birthTimeVal,
                        location: locationVal,
                        language: window.currentLanguage || 'zh-CN'
                    })
                });
                
                const result = await response.json();
                if (response.ok && result.report_url) {
                    if (reportWindow) {
                        reportWindow.location.href = result.report_url;
                    } else {
                        window.open(result.report_url, '_blank');
                    }
                } else {
                    if (reportWindow) reportWindow.close();
                    alert('Failed to generate report: ' + (result.error || 'Unknown error'));
                }
            } catch (error) {
                console.error('Error generating report:', error);
                if (reportWindow) reportWindow.close();
                alert('An error occurred during report generation.');
            } finally {
                viewFullReportBtn.disabled = false;
                viewFullReportBtn.innerHTML = originalText;
            }
        });
    }
});
