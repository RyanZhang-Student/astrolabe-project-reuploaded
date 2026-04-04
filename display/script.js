// Star generator for background
function createStars() {
    const starsContainer = document.getElementById('stars');
    const starCount = 150;

    for (let i = 0; i < starCount; i++) {
        const star = document.createElement('div');
        star.className = 'star';

        const size = Math.random() * 3 + 'px';
        star.style.width = size;
        star.style.height = size;

        star.style.left = Math.random() * 100 + '%';
        star.style.top = Math.random() * 100 + '%';

        star.style.setProperty('--duration', (Math.random() * 3 + 2) + 's');
        star.style.animationDelay = Math.random() * 5 + 's';

        starsContainer.appendChild(star);
    }
}

// Time Picker Logic (Global Object for direct access)
window.timePicker = {
    modal: null,
    columns: {},
    dateInput: null,
    timeInput: null,

    init() {
        console.log('TimePicker: Initializing...');
        this.modal = document.getElementById('time-picker-modal');
        this.dateInput = document.getElementById('birth-date');
        this.timeInput = document.getElementById('birth-time');

        if (!this.modal) {
            console.error('TimePicker: Modal element not found!');
            return;
        }

        this.columns = {
            year: { el: document.querySelector('#picker-year .picker-scroll'), range: [1900, 2100], current: 2000, isInfinite: false },
            month: { el: document.querySelector('#picker-month .picker-scroll'), range: [1, 12], current: new Date().getMonth() + 1, isInfinite: true },
            day: { el: document.querySelector('#picker-day .picker-scroll'), range: [1, 31], current: new Date().getDate(), isInfinite: true },
            hour: { el: document.querySelector('#picker-hour .picker-scroll'), range: [0, 23], current: 12, isInfinite: true },
            minute: { el: document.querySelector('#picker-minute .picker-scroll'), range: [0, 59], current: 0, isInfinite: true }
        };

        // Populate and attach scroll listeners
        for (const [key, config] of Object.entries(this.columns)) {
            this.populateColumn(key, config);
            config.el.addEventListener('scroll', () => this.handleScroll(key));
        }

        // Initial check for day range
        this.checkDayRange();

        console.log('TimePicker: Ready.');
        this.hide(); // Ensure hidden on start
    },

    populateColumn(key, config) {
        const [start, end] = config.range;
        const count = end - start + 1;
        const repetitions = config.isInfinite ? 10 : 1;
        let html = '';

        for (let r = 0; r < repetitions; r++) {
            for (let i = start; i <= end; i++) {
                const val = i.toString().padStart(2, '0');
                html += `<div class="picker-item" data-value="${i}">${val}</div>`;
            }
        }
        config.el.innerHTML = html;
        config.itemCount = count;
        config.itemHeight = 40;

        setTimeout(() => {
            const middleRep = Math.floor(repetitions / 2);
            const index = (config.current - start) + (middleRep * count);
            config.el.scrollTop = index * config.itemHeight;
            this.updateSelection(config.el);
        }, 100);
    },

    handleScroll(key) {
        const config = this.columns[key];
        if (config.isInfinite) {
            const setHeight = config.itemCount * config.itemHeight;
            const scrollTop = config.el.scrollTop;

            // Jump threshold: if we are within 2 sets from top or bottom, jump to the middle
            if (scrollTop < setHeight * 2) {
                config.el.scrollTop = scrollTop + setHeight * 4;
            } else if (scrollTop > config.el.scrollHeight - setHeight * 3) {
                config.el.scrollTop = scrollTop - setHeight * 4;
            }
        }

        if (this.scrollTimeout) clearTimeout(this.scrollTimeout);
        this.scrollTimeout = setTimeout(() => {
            this.updateSelection(config.el);
            // If year or month changes, update day range
            if (key === 'year' || key === 'month') {
                this.checkDayRange();
            }
        }, 50);
    },

    updateSelection(scrollEl) {
        const index = Math.round(scrollEl.scrollTop / 40);
        const items = scrollEl.querySelectorAll('.picker-item');
        items.forEach((item, i) => {
            if (i === index) item.classList.add('selected');
            else item.classList.remove('selected');
        });
    },

    getSelectedValue(key) {
        const config = this.columns[key];
        const index = Math.round(config.el.scrollTop / 40);
        const items = config.el.querySelectorAll('.picker-item');
        return items[index] ? parseInt(items[index].dataset.value) : config.range[0];
    },

    show(e) {
        if (e) { e.preventDefault(); e.stopPropagation(); }
        console.log('TimePicker: Showing modal');
        this.modal.classList.remove('hidden');
        this.modal.style.setProperty('display', 'flex', 'important');
        this.modal.style.setProperty('visibility', 'visible', 'important');
        this.modal.style.setProperty('opacity', '1', 'important');
        this.modal.style.setProperty('pointer-events', 'auto', 'important');
        document.body.style.overflow = 'hidden';

        // Refresh scroll positions when showing
        for (const [key, config] of Object.entries(this.columns)) {
            const [start, end] = config.range;
            const count = end - start + 1;
            const repetitions = config.isInfinite ? 10 : 1;
            const middleRep = Math.floor(repetitions / 2);
            const index = (config.current - start) + (middleRep * count);
            config.el.scrollTop = index * 40; // match itemHeight
            this.updateSelection(config.el);
        }
    },

    hide(e) {
        if (e) { e.preventDefault(); e.stopPropagation(); }
        console.log('TimePicker: Hiding modal');
        this.modal.classList.add('hidden');
        this.modal.style.setProperty('display', 'none', 'important');
        this.modal.style.setProperty('visibility', 'hidden', 'important');
        this.modal.style.setProperty('opacity', '0', 'important');
        this.modal.style.setProperty('pointer-events', 'none', 'important');
        document.body.style.overflow = 'auto';
    },

    isLeapYear(year) {
        return (year % 4 === 0 && year % 100 !== 0) || (year % 400 === 0);
    },

    getMaxDay(month, year) {
        if (month === 2) {
            return this.isLeapYear(year) ? 29 : 28;
        }
        if ([4, 6, 9, 11].includes(month)) {
            return 30;
        }
        return 31;
    },

    checkDayRange() {
        const year = this.getSelectedValue('year');
        const month = this.getSelectedValue('month');
        const maxDay = this.getMaxDay(month, year);
        const dayConfig = this.columns.day;

        if (dayConfig.range[1] !== maxDay) {
            console.log(`TimePicker: Updating day range to 1-${maxDay}`);
            const currentDay = this.getSelectedValue('day');
            dayConfig.range[1] = maxDay;
            dayConfig.current = Math.min(currentDay, maxDay);

            // Re-populate the day column. populateColumn has its own 100ms timeout
            // to set the scrollTop based on dayConfig.current.
            this.populateColumn('day', dayConfig);
        }
    },

    confirm(e) {
        if (e) { e.preventDefault(); e.stopPropagation(); }
        console.log('TimePicker: Confirming selection');
        const year = this.getSelectedValue('year');
        const month = this.getSelectedValue('month');
        const day = this.getSelectedValue('day');
        const hour = this.getSelectedValue('hour').toString().padStart(2, '0');
        const minute = this.getSelectedValue('minute').toString().padStart(2, '0');

        // Validation is now handled dynamically in the scroll picker,
        // so we don't need additional checks here.

        const monthStr = month.toString().padStart(2, '0');
        const dayStr = day.toString().padStart(2, '0');

        this.dateInput.value = `${year}-${monthStr}-${dayStr}`;
        this.timeInput.value = `${hour}:${minute}`;
        this.hide();
    }
};

document.addEventListener('DOMContentLoaded', () => {
    createStars();
    window.timePicker.init();

    const form = document.getElementById('astrolabe-form');
    const submitBtn = document.getElementById('submit-btn');
    const btnText = submitBtn.querySelector('.btn-text');
    const loader = document.getElementById('loader');
    const resultContainer = document.getElementById('result-container');
    const reportLink = document.getElementById('report-link');

    // Gender selection logic
    const genderBoxes = document.querySelectorAll('.gender-box');
    const genderInput = document.getElementById('gender');

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
        });
    });

    const locationInput = document.getElementById('location');
    const autocompleteList = document.getElementById('autocomplete-list');

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

        content.innerHTML = `
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

    // Close modal on click outside
    window.addEventListener('click', (e) => {
        const modal = document.getElementById('starModal');
        if (e.target === modal) {
            window.closeStarModal();
        }
    });

    // Handle form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        if (!genderInput.value) {
            alert('Please select a gender.');
            return;
        }

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
                    dob: dobFormatted
                })
            });

            const result = await response.json();

            if (response.ok) {
                btnText.style.opacity = '1';
                loader.style.display = 'none';
                submitBtn.disabled = false;

                resultContainer.classList.remove('hidden');
                reportLink.textContent = `View Report for ${name}`;
                reportLink.href = `/results/report_${name.toUpperCase()}.html`;

                // Render Chart Photo via Canvas to ensure it is a raster image, not decipherable HTML/SVG
                if (result.chart_svg_base64) {
                    const img = new Image();
                    img.onload = function () {
                        const canvas = document.createElement('canvas');
                        canvas.width = 800; // SVG viewBox is 800x800
                        canvas.height = 800;
                        const ctx = canvas.getContext('2d');

                        // Draw a solid background so it isn't transparent (assuming light theme chart)
                        ctx.fillStyle = '#ffffff';
                        ctx.fillRect(0, 0, canvas.width, canvas.height);

                        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

                        const ptrUrl = canvas.toDataURL('image/png');
                        const chartImg = document.getElementById('natal-chart-img');
                        chartImg.src = ptrUrl;
                        document.getElementById('chart-image-container').classList.remove('hidden');
                    };
                    img.src = 'data:image/svg+xml;base64,' + result.chart_svg_base64;
                }

                // Render Star Conjunctions
                if (result.star_stats) {
                    window.starData = result.star_aspects || [];
                    window.renderStarStats(result.star_stats);
                }
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
});
