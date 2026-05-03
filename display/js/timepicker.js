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
