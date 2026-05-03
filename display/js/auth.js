document.addEventListener('DOMContentLoaded', () => {
    // Login Popup Logic
    const loginBtn = document.getElementById('login-btn');
    if (loginBtn) {
        loginBtn.addEventListener('click', () => {
            if(window.saveFormState) window.saveFormState(false);
            const width = 500;
            const height = 650;
            const left = (window.innerWidth - width) / 2 + window.screenX;
            const top = (window.innerHeight - height) / 2 + window.screenY;
            window.open('/login', 'google_login', `width=${width},height=${height},top=${top},left=${left}`);
        });
    }

    // Profile Popup Logic
    const userBtn = document.getElementById('user-btn');
    const profilePopup = document.getElementById('profile-popup');
    const profileOverlay = document.getElementById('profile-overlay');

    if (userBtn && profilePopup && profileOverlay) {
        const toggleProfile = (show) => {
            if (show) {
                profilePopup.classList.remove('hidden');
                profileOverlay.classList.add('active');
            } else {
                profilePopup.classList.add('hidden');
                profileOverlay.classList.remove('active');
            }
        };

        userBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const isHidden = profilePopup.classList.contains('hidden');
            toggleProfile(isHidden);
        });

        profileOverlay.addEventListener('click', () => toggleProfile(false));
        
        // Prevent clicks inside popup from closing it, but allow links and buttons to work
        profilePopup.addEventListener('click', (e) => {
            if (e.target.closest('a, button')) return;
            e.stopPropagation();
        });
    }
});
});
