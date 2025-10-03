class LoginManager {
    constructor() {
        this.selectedAvatar = null;
        this.init();
    }

    init() {
        this.setupAvatarSelection();
        this.setupFormSubmission();
    }

    setupAvatarSelection() {
        const avatarOptions = document.querySelectorAll('.avatar-option');
        
        avatarOptions.forEach(option => {
            option.addEventListener('click', () => {
                // Remove selected class from all options
                avatarOptions.forEach(opt => opt.classList.remove('selected'));
                
                // Add selected class to clicked option
                option.classList.add('selected');
                this.selectedAvatar = option.dataset.avatar;
            });
        });
    }

    setupFormSubmission() {
        const form = document.getElementById('loginForm');
        
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleLogin();
        });
    }

    handleLogin() {
        const userName = document.getElementById('userName').value.trim();
        
        if (!userName) {
            this.showNotification('Lütfen adınızı girin.', 'error');
            return;
        }

        if (!this.selectedAvatar) {
            this.showNotification('Lütfen bir avatar seçin.', 'error');
            return;
        }

        // Store user data in localStorage
        const userData = {
            name: userName,
            avatar: this.selectedAvatar,
            userId: 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 5)
        };
        
        localStorage.setItem('tvPlusUser', JSON.stringify(userData));
        
        this.showNotification('Giriş başarılı! Yönlendiriliyorsunuz...', 'success');
        
        // Redirect to register page after a short delay
        setTimeout(() => {
            window.location.href = '/register';
        }, 1500);
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // Style the notification
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 10px;
            color: white;
            font-weight: 600;
            z-index: 1000;
            animation: slideIn 0.3s ease;
            max-width: 300px;
        `;
        
        // Set background color based on type
        if (type === 'success') {
            notification.style.background = 'linear-gradient(135deg, #28a745, #20c997)';
        } else if (type === 'error') {
            notification.style.background = 'linear-gradient(135deg, #dc3545, #e74c3c)';
        } else {
            notification.style.background = 'linear-gradient(135deg, #1e3c72, #2a5298)';
        }
        
        // Add to page
        document.body.appendChild(notification);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Initialize login manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new LoginManager();
});

// Global function for register button
function goToRegister() {
    window.location.href = '/register';
}
