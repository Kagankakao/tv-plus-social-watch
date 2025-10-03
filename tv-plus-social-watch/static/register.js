class RegisterManager {
    constructor() {
        this.userData = null;
        this.init();
    }

    init() {
        this.loadUserData();
        this.setupEventListeners();
    }

    loadUserData() {
        const storedUser = localStorage.getItem('tvPlusUser');
        if (storedUser) {
            this.userData = JSON.parse(storedUser);
        } else {
            // If no user data, redirect to login
            window.location.href = '/login';
        }
    }

    setupEventListeners() {
        const roomCodeInput = document.getElementById('roomCode');
        
        // Allow only alphanumeric characters for room code
        roomCodeInput.addEventListener('input', (e) => {
            e.target.value = e.target.value.replace(/[^a-zA-Z0-9]/g, '').toUpperCase();
        });
        
        // Handle Enter key in room code input
        roomCodeInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.joinRoom();
            }
        });
    }

    createRoom() {
        if (!this.userData) {
            this.showNotification('Kullanıcı bilgileri bulunamadı. Lütfen tekrar giriş yapın.', 'error');
            setTimeout(() => {
                window.location.href = '/login';
            }, 2000);
            return;
        }

        // Generate a random room code
        const roomCode = this.generateRoomCode();
        
        // Create room data
        const roomData = {
            roomId: roomCode,
            hostId: this.userData.userId,
            hostName: this.userData.name,
            hostAvatar: this.userData.avatar,
            isHost: true,
            createdAt: new Date().toISOString()
        };
        
        // Store room data
        localStorage.setItem('tvPlusRoom', JSON.stringify(roomData));
        
        this.showNotification(`Oda oluşturuldu! Oda kodu: ${roomCode}`, 'success');
        
        // Redirect to main app after a short delay
        setTimeout(() => {
            window.location.href = '/app';
        }, 2000);
    }

    joinRoom() {
        const roomCode = document.getElementById('roomCode').value.trim().toUpperCase();
        
        if (!roomCode) {
            this.showNotification('Lütfen oda kodunu girin.', 'error');
            return;
        }

        if (!this.userData) {
            this.showNotification('Kullanıcı bilgileri bulunamadı. Lütfen tekrar giriş yapın.', 'error');
            setTimeout(() => {
                window.location.href = '/login';
            }, 2000);
            return;
        }

        // Create room data for joining
        const roomData = {
            roomId: roomCode,
            hostId: null, // Will be determined when joining
            hostName: null,
            hostAvatar: null,
            isHost: false,
            joinedAt: new Date().toISOString()
        };
        
        // Store room data
        localStorage.setItem('tvPlusRoom', JSON.stringify(roomData));
        
        this.showNotification(`${roomCode} odasına katılıyorsunuz...`, 'success');
        
        // Redirect to main app after a short delay
        setTimeout(() => {
            window.location.href = '/app';
        }, 1500);
    }

    generateRoomCode() {
        const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
        let result = '';
        for (let i = 0; i < 6; i++) {
            result += chars.charAt(Math.floor(Math.random() * chars.length));
        }
        return result;
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

// Initialize register manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new RegisterManager();
});

// Global functions for buttons
function createRoom() {
    const manager = new RegisterManager();
    manager.createRoom();
}

function joinRoom() {
    const manager = new RegisterManager();
    manager.joinRoom();
}

function goBack() {
    window.location.href = '/login';
}
