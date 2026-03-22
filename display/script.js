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

// Time Picker Logic
class TimePicker {
    constructor() {
        this.modal = document.getElementById('time-picker-modal');
        this.confirmBtn = document.getElementById('confirm-selection');
        this.closeBtn = document.getElementById('close-picker');
        this.dateInput = document.getElementById('birth-date');
        this.timeInput = document.getElementById('birth-time');

        this.columns = {
            year: { el: document.querySelector('#picker-year .picker-scroll'), range: [1900, 2100], current: new Date().getFullYear() },
            month: { el: document.querySelector('#picker-month .picker-scroll'), range: [1, 12], current: new Date().getMonth() + 1 },
            day: { el: document.querySelector('#picker-day .picker-scroll'), range: [1, 31], current: new Date().getDate() },
            hour: { el: document.querySelector('#picker-hour .picker-scroll'), range: [0, 23], current: 12 },
            minute: { el: document.querySelector('#picker-minute .picker-scroll'), range: [0, 59], current: 0 }
        };

        this.init();
    }

    init() {
        // Populate columns
        for (const [key, config] of Object.entries(this.columns)) {
            this.populateColumn(config);
            config.el.addEventListener('scroll', () => this.handleScroll(key));
        }

        // Open modal
        this.dateInput.addEventListener('click', () => this.show());
        this.timeInput.addEventListener('click', () => this.show());

        // Close modal
        this.closeBtn.addEventListener('click', () => this.hide());
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) this.hide();
        });

        // Confirm selection
        this.confirmBtn.addEventListener('click', () => {
            this.applySelection();
            this.hide();
        });
    }

    populateColumn(config) {
        const [start, end] = config.range;
        let html = '';
        for (let i = start; i <= end; i++) {
            const val = i.toString().padStart(2, '0');
            html += `<div class="picker-item" data-value="${i}">${val}</div>`;
        }
        config.el.innerHTML = html;

        // Initial scroll position
        setTimeout(() => {
            const index = config.current - start;
            config.el.scrollTop = index * 40;
            this.updateSelection(config.el);
        }, 100);
    }

    handleScroll(key) {
        if (this.scrollTimeout) clearTimeout(this.scrollTimeout);
        this.scrollTimeout = setTimeout(() => {
            this.updateSelection(this.columns[key].el);
        }, 50);
    }

    updateSelection(scrollEl) {
        const index = Math.round(scrollEl.scrollTop / 40);
        const items = scrollEl.querySelectorAll('.picker-item');
        items.forEach((item, i) => {
            if (i === index) {
                item.classList.add('selected');
            } else {
                item.classList.remove('selected');
            }
        });
    }

    getSelectedValue(key) {
        const config = this.columns[key];
        const index = Math.round(config.el.scrollTop / 40);
        const items = config.el.querySelectorAll('.picker-item');
        return items[index] ? parseInt(items[index].dataset.value) : config.range[0];
    }

    applySelection() {
        const year = this.getSelectedValue('year');
        const month = this.getSelectedValue('month').toString().padStart(2, '0');
        const day = this.getSelectedValue('day').toString().padStart(2, '0');
        const hour = this.getSelectedValue('hour').toString().padStart(2, '0');
        const minute = this.getSelectedValue('minute').toString().padStart(2, '0');

        this.dateInput.value = `${year}-${month}-${day}`;
        this.timeInput.value = `${hour}:${minute}`;
    }

    show() {
        this.modal.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }

    hide() {
        this.modal.classList.add('hidden');
        document.body.style.overflow = 'auto';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    createStars();
    new TimePicker();

    const form = document.getElementById('astrolabe-form');
    const submitBtn = document.getElementById('submit-btn');
    const btnText = submitBtn.querySelector('.btn-text');
    const loader = document.getElementById('loader');
    const resultContainer = document.getElementById('result-container');
    const reportLink = document.getElementById('report-link');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // UI Feedback
        btnText.style.opacity = '0';
        loader.style.display = 'block';
        submitBtn.disabled = true;
        resultContainer.classList.add('hidden');

        // Collect Data
        const name = document.getElementById('name').value;
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
