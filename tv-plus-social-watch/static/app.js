class TVPlusApp {
    constructor() {
        this.currentTime = 0;
        this.duration = 0; // Will be set from selected content
        this.isPlaying = false;
        this.roomId = null; // Will be loaded from localStorage
        this.userId = null; // Will be loaded from localStorage
        this.lastMessageTime = 0;
        this.websocket = null;
        this.userData = null;
        this.roomData = null;
        this.isHost = false;
        this.votingComplete = false;
        this.roomUserCount = 0;
        this.selectedContent = null;
        this.partyStartTime = Date.now();
        this.serverHealth = 'connecting';
        this.lastPingTime = 0;
        
        this.loadUserAndRoomData();
        this.init();
    }

    loadUserAndRoomData() {
        // Load user data from localStorage
        const storedUser = localStorage.getItem('tvPlusUser');
        if (storedUser) {
            this.userData = JSON.parse(storedUser);
            this.userId = this.userData.userId;
        } else {
            // Create temporary user for testing
            this.userData = {
                userId: 'user_' + Math.random().toString(36).substr(2, 9),
                name: 'Kullanıcı',
                avatar: '👤'
            };
            this.userId = this.userData.userId;
            localStorage.setItem('tvPlusUser', JSON.stringify(this.userData));
            console.log('Created temporary user:', this.userId);
        }

        // Load room data from localStorage
        const storedRoom = localStorage.getItem('tvPlusRoom');
        if (storedRoom) {
            this.roomData = JSON.parse(storedRoom);
            this.roomId = this.roomData.roomId;
            this.isHost = this.roomData.isHost;
        } else {
            // Use default room for testing
            this.roomData = {
                roomId: 'room_1',
                title: 'Akşam Film Gecesi',
                isHost: false
            };
            this.roomId = 'room_1';
            this.isHost = false;
            localStorage.setItem('tvPlusRoom', JSON.stringify(this.roomData));
            console.log('Using default room: room_1');
        }
    }

    init() {
        // Check if we have required data
        if (!this.userData || !this.roomData) {
            return;
        }

        this.setupTabs();
        this.setupVideoControls();
        this.setupChat();
        this.setupVoting();
        this.setupExpenses();
        this.connectWebSocket();
        this.startTimer();
        this.updateUIWithUserData();
        this.checkRoomStatus();
        this.checkVotingStatus();
        this.startPartyTimer();
        this.startHealthMonitoring();
        
        // Poll room status and voting every 3 seconds
        setInterval(() => {
            this.checkRoomStatus();
            this.checkVotingStatus();
        }, 3000);
        
        console.log('TV+ App initialized with user:', this.userId, 'room:', this.roomId, 'isHost:', this.isHost);
    }

    // Tab Management
    setupTabs() {
        const tabBtns = document.querySelectorAll('.tab-btn');
        const tabContents = document.querySelectorAll('.tab-content');

        tabBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const targetTab = btn.dataset.tab;
                
                // Remove active class from all
                tabBtns.forEach(b => b.classList.remove('active'));
                tabContents.forEach(c => c.classList.remove('active'));
                
                // Add active class to clicked
                btn.classList.add('active');
                document.getElementById(targetTab + '-tab').classList.add('active');
            });
        });
    }

    // Video Controls
    setupVideoControls() {
        const playPauseBtn = document.getElementById('play-pause-btn');
        const playIcon = document.getElementById('play-btn');
        const progressBar = document.querySelector('.progress-bar');
        const syncBtn = document.getElementById('sync-btn');

        // All users can control video (not just host)
        playPauseBtn.addEventListener('click', () => this.togglePlayPause());
        playIcon.addEventListener('click', () => this.togglePlayPause());
        progressBar.addEventListener('click', (e) => this.seek(e));
        syncBtn.addEventListener('click', () => this.syncVideo());

        // Update progress every second
        setInterval(() => {
            if (this.isPlaying) {
                this.currentTime += 1;
                this.updateProgress();
            }
        }, 1000);
    }

    togglePlayPause() {
        // Check if voting is complete before allowing playback
        if (!this.votingComplete) {
            this.showNotification('⚠️ Oylama tamamlanmadan video oynatılamaz!');
            return;
        }
        
        this.isPlaying = !this.isPlaying;
        const playPauseBtn = document.getElementById('play-pause-btn');
        const playIcon = document.getElementById('play-btn');
        
        if (this.isPlaying) {
            playPauseBtn.textContent = '⏸ Pause';
            playIcon.textContent = '⏸';
        } else {
            playPauseBtn.textContent = '▶ Play';
            playIcon.textContent = '▶';
        }

        // Send WebSocket event
        this.sendWebSocketEvent('play_pause', { 
            action: this.isPlaying ? 'play' : 'pause',
            position: this.currentTime 
        });
    }

    seek(e) {
        const progressBar = e.currentTarget;
        const rect = progressBar.getBoundingClientRect();
        const percentage = (e.clientX - rect.left) / rect.width;
        this.currentTime = Math.floor(percentage * this.duration);
        this.updateProgress();

        // Send WebSocket event
        this.sendWebSocketEvent('seek', { position: this.currentTime });
    }

    syncVideo() {
        // Request sync from server
        this.sendWebSocketEvent('sync_request', { user_id: this.userId });
        
        // Show feedback
        const syncBtn = document.getElementById('sync-btn');
        const originalText = syncBtn.textContent;
        syncBtn.textContent = '✓ Senkronize edildi';
        setTimeout(() => {
            syncBtn.textContent = originalText;
        }, 2000);
    }

    updateProgress() {
        const progress = document.getElementById('progress');
        const timeDisplay = document.getElementById('time-display');
        
        const percentage = (this.currentTime / this.duration) * 100;
        progress.style.width = percentage + '%';
        
        const currentFormatted = this.formatTime(this.currentTime);
        const durationFormatted = this.formatTime(this.duration);
        timeDisplay.textContent = `${currentFormatted} / ${durationFormatted}`;
    }

    formatTime(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }

    // Chat System
    setupChat() {
        const messageInput = document.getElementById('message-input');
        const sendBtn = document.getElementById('send-btn');
        const emojiButtons = document.querySelectorAll('.emoji-btn');

        sendBtn.addEventListener('click', () => this.sendMessage());
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });

        emojiButtons.forEach(btn => {
            btn.addEventListener('click', () => this.sendEmoji(btn.dataset.emoji));
        });
    }

    sendMessage() {
        const messageInput = document.getElementById('message-input');
        const message = messageInput.value.trim();
        
        if (!message) return;
        
        // Rate limiting check
        const now = Date.now();
        if (now - this.lastMessageTime < 2000) {
            this.showNotification('Çok hızlı mesaj gönderiyorsunuz. 2 saniye bekleyin.');
            return;
        }
        
        this.lastMessageTime = now;
        messageInput.value = '';
        
        // Add to chat locally with user's name
        const displayName = this.userData && this.userData.name ? this.userData.name : this.userId;
        this.addChatMessage(displayName, message);
        
        // Send via WebSocket
        this.sendWebSocketEvent('chat', { message, user_id: this.userId });
    }

    sendEmoji(emoji) {
        // Rate limiting check
        const now = Date.now();
        if (now - this.lastMessageTime < 2000) {
            this.showNotification('Çok hızlı emoji gönderiyorsunuz. 2 saniye bekleyin.');
            return;
        }
        
        this.lastMessageTime = now;
        
        // Add to chat locally with user's name
        const displayName = this.userData && this.userData.name ? this.userData.name : this.userId;
        this.addChatMessage(displayName, emoji);
        
        // Send via WebSocket
        this.sendWebSocketEvent('emoji', { emoji, user_id: this.userId });
    }

    addChatMessage(username, text) {
        const chatMessages = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message';
        messageDiv.innerHTML = `
            <span class="username">${username}:</span>
            <span class="text">${text}</span>
        `;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Voting System
    setupVoting() {
        // Load candidates initially
        this.loadCandidates();
        
        // Setup complete voting button (host only)
        const completeBtn = document.getElementById('complete-voting-btn');
        if (completeBtn && this.isHost) {
            completeBtn.style.display = 'block';
            completeBtn.addEventListener('click', () => this.completeVoting());
        }
    }

    async loadCandidates() {
        try {
            console.log(`Loading candidates for room: ${this.roomId}`);
            const response = await fetch(`/votes/${this.roomId}/candidates`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('Candidates loaded:', data);
            
            this.updateCandidatesUI(data.candidates || []);
            this.loadVoteTally();
        } catch (error) {
            console.error('Error loading candidates:', error);
            this.showNotification('❌ Aday içerikler yüklenemedi. Veritabanı bağlantısını kontrol edin.');
            this.updateCandidatesUI([]);
        }
    }

    updateCandidatesUI(candidates) {
        const candidatesList = document.getElementById('candidates-list');
        candidatesList.innerHTML = '';
        
        if (!candidates || candidates.length === 0) {
            candidatesList.innerHTML = `
                <div style="padding: 2rem; text-align: center;">
                    <p style="color: #999; margin-bottom: 1rem;">Henüz aday içerik eklenmedi.</p>
                    <small style="color: #666;">Host'un oylama için içerik eklemesi bekleniyor.</small>
                </div>
            `;
            return;
        }
        
        candidates.forEach(candidate => {
            const div = document.createElement('div');
            div.className = 'candidate-item';
            div.innerHTML = `
                <div style="flex: 1;">
                    <div style="font-weight: 600; color: #fddb3a; font-size: 1rem;">${candidate.title}</div>
                    <small style="color: #999;">${candidate.type} • ${candidate.duration_min} dk</small>
                </div>
                <div style="display: flex; align-items: center; gap: 0.75rem;">
                    <span class="vote-count" data-content="${candidate.content_id}" style="min-width: 50px;">0 oy</span>
                    <button class="vote-btn" data-content="${candidate.content_id}">Oy Ver</button>
                </div>
            `;
            candidatesList.appendChild(div);
        });
        
        // Re-attach vote button listeners
        const voteButtons = document.querySelectorAll('.vote-btn');
        voteButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const contentId = btn.dataset.content;
                this.vote(contentId);
            });
        });
        
        console.log(`Loaded ${candidates.length} candidates for voting`);
    }

    async vote(contentId) {
        // Check room user count
        if (this.roomUserCount < 2) {
            this.showNotification('⚠️ Oylama için odada en az 2 kişi olmalı!');
            return;
        }
        
        try {
            const response = await fetch('/votes', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    room_id: this.roomId,
                    content_id: contentId,
                    user_id: this.userId
                })
            });
            
            if (response.ok) {
                this.showNotification('✓ Oyunuz kaydedildi!');
                this.loadVoteTally();
                await this.checkVotingStatus();
                
                // Notify other users via WebSocket
                this.sendWebSocketEvent('vote_update', {
                    user_id: this.userId,
                    content_id: contentId
                });
            } else {
                this.showNotification('❌ Oy kaydedilemedi.');
            }
        } catch (error) {
            console.error('Error voting:', error);
            this.showNotification('❌ Bir hata oluştu.');
        }
    }

    async loadVoteTally() {
        try {
            const response = await fetch(`/votes/${this.roomId}/tally`);
            const data = await response.json();
            this.updateVoteCounts(data.tally || []);
        } catch (error) {
            console.error('Error loading vote tally:', error);
        }
    }
    
    updateVoteCounts(tally) {
        tally.forEach(item => {
            const voteCountElement = document.querySelector(`.vote-count[data-content="${item.content_id}"]`);
            if (voteCountElement) {
                const votes = parseInt(item.votes);
                voteCountElement.textContent = `${votes} oy`;
                voteCountElement.style.color = votes > 0 ? '#fddb3a' : '#999';
                voteCountElement.style.fontWeight = votes > 0 ? '600' : 'normal';
            }
        });
    }

    // Expense Management
    setupExpenses() {
        const addExpenseBtn = document.getElementById('add-expense-btn');
        
        addExpenseBtn.addEventListener('click', () => this.addExpense());
        
        this.loadExpenses();
    }

    async addExpense() {
        const desc = document.getElementById('expense-desc').value.trim();
        const amount = parseFloat(document.getElementById('expense-amount').value);
        const weight = parseFloat(document.getElementById('expense-weight').value) || 1.0;
        
        if (!desc || !amount || amount <= 0) {
            this.showNotification('Lütfen geçerli açıklama ve tutar girin.');
            return;
        }
        
        if (weight <= 0) {
            this.showNotification('Ağırlık 0\'dan büyük olmalıdır.');
            return;
        }
        
        try {
            const response = await fetch(`/rooms/${this.roomId}/expenses`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: this.userId,
                    amount: amount,
                    note: desc,
                    weight: weight
                })
            });
            
            if (response.ok) {
                document.getElementById('expense-desc').value = '';
                document.getElementById('expense-amount').value = '';
                document.getElementById('expense-weight').value = '1.0';
                this.showNotification('✓ Masraf eklendi!');
                this.loadExpenses();
            } else {
                this.showNotification('❌ Masraf eklenemedi.');
            }
        } catch (error) {
            console.error('Error adding expense:', error);
            this.showNotification('❌ Bir hata oluştu.');
        }
    }

    async loadExpenses() {
        try {
            const response = await fetch(`/rooms/${this.roomId}/expenses`);
            const data = await response.json();
            this.updateExpensesUI(data.expenses || []);
            
            const balanceResponse = await fetch(`/rooms/${this.roomId}/balances`);
            const balanceData = await balanceResponse.json();
            this.updateBalancesUI(balanceData.per_user || [], balanceData.totals || 0);
        } catch (error) {
            console.error('Error loading expenses:', error);
            this.updateExpensesUI([]);
            this.updateBalancesUI([], 0);
        }
    }

    updateExpensesUI(expenses) {
        const expensesList = document.getElementById('expenses-list');
        expensesList.innerHTML = '<h4 style="color: #fddb3a;">📋 Masraflar:</h4>';
        
        if (expenses.length === 0) {
            expensesList.innerHTML += '<p style="color: #999; text-align: center; padding: 1rem;">Henüz masraf eklenmedi.</p>';
            return;
        }
        
        expenses.forEach(expense => {
            const div = document.createElement('div');
            div.className = 'expense-item';
            const weight = parseFloat(expense.weight);
            const weightText = weight === 1.0 ? '' : ` (x${weight.toFixed(1)})`;
            const userName = this.getUserDisplayName(expense.user_id);
            div.innerHTML = `
                <div>
                    <div style="font-weight: 600;">${expense.note}</div>
                    <small style="color: #999;">👤 ${userName}${weightText}</small>
                </div>
                <span style="color: #fddb3a; font-weight: 600;">₺${parseFloat(expense.amount).toFixed(2)}</span>
            `;
            expensesList.appendChild(div);
        });
    }

    updateBalancesUI(balances, totals) {
        const balancesDiv = document.getElementById('balances');
        balancesDiv.innerHTML = '<h4 style="color: #fddb3a;">💰 Net Bakiyeler:</h4>';
        
        if (balances.length === 0) {
            balancesDiv.innerHTML += '<p style="color: #999; text-align: center; padding: 1rem;">Henüz bakiye hesaplanmadı.</p>';
            return;
        }
        
        balances.forEach(balance => {
            const div = document.createElement('div');
            div.className = 'balance-item';
            const net = parseFloat(balance.net);
            const paid = parseFloat(balance.paid);
            const owed = parseFloat(balance.owed);
            const color = net >= 0 ? '#28a745' : '#dc3545';
            const statusIcon = net >= 0 ? '✓' : '⚠';
            const statusText = net >= 0 ? 'Alacaklı' : 'Borçlu';
            const userName = this.getUserDisplayName(balance.user_id);
            
            div.innerHTML = `
                <div>
                    <div style="font-weight: 600;">${userName}</div>
                    <small style="color: #999;">Ödedi: ₺${paid} | Borç: ₺${owed}</small>
                </div>
                <div style="text-align: right;">
                    <div style="color: ${color}; font-weight: 700; font-size: 1.1rem;">${statusIcon} ₺${Math.abs(net).toFixed(2)}</div>
                    <small style="color: ${color};">${statusText}</small>
                </div>
            `;
            balancesDiv.appendChild(div);
        });
        
        // Add total summary
        const summaryDiv = document.createElement('div');
        summaryDiv.style.cssText = 'margin-top: 1rem; padding: 0.75rem; background: rgba(253, 219, 58, 0.1); border-radius: 4px; border-left: 3px solid #fddb3a;';
        summaryDiv.innerHTML = `
            <strong style="color: #fddb3a;">📊 Toplam Masraf:</strong> 
            <span style="color: white; font-size: 1.2rem; font-weight: 700;">₺${balances.reduce((sum, b) => sum + parseFloat(b.paid), 0).toFixed(2)}</span>
        `;
        balancesDiv.appendChild(summaryDiv);
    }

    // Room Status & Voting Status
    async checkRoomStatus() {
        try {
            const response = await fetch(`/rooms/${this.roomId}/status`);
            const data = await response.json();
            this.roomUserCount = data.user_count || 0;
            
            // Update UI
            const roomUsersElement = document.getElementById('room-users');
            if (roomUsersElement) {
                roomUsersElement.textContent = `👥 ${this.roomUserCount} kişi`;
            }
        } catch (error) {
            console.error('Error checking room status:', error);
        }
    }
    
    async checkVotingStatus() {
        try {
            const response = await fetch(`/votes/${this.roomId}/winner`);
            const data = await response.json();
            
            if (data.winner) {
                this.votingComplete = true;
                this.selectedContent = data.winner;
            } else {
                this.votingComplete = false;
                this.selectedContent = null;
            }
            
            // Update voting progress UI
            this.updateVotingProgress(data);
            this.updateSelectedContent();
        } catch (error) {
            console.error('Error checking voting status:', error);
            this.updateSelectedContent();
        }
    }
    
    updateVotingProgress(data) {
        const votingInfoDiv = document.querySelector('.voting-info');
        if (!votingInfoDiv) return;
        
        const totalVoted = data.total_voted || 0;
        const roomUserCount = data.room_user_count || this.roomUserCount;
        const votingStatus = data.voting_status || 'pending';
        
        if (votingStatus === 'complete') {
            votingInfoDiv.innerHTML = `
                <small style="color: #28a745;">
                    ✅ Oylama tamamlandı! ${totalVoted}/${roomUserCount} kişi oy kullandı.
                </small>
            `;
            votingInfoDiv.style.background = 'rgba(40, 167, 69, 0.1)';
            votingInfoDiv.style.borderLeftColor = '#28a745';
        } else {
            votingInfoDiv.innerHTML = `
                <small style="color: #fddb3a;">
                    ⏳ Oylama devam ediyor... ${totalVoted}/${roomUserCount} kişi oy kullandı. Tüm üyelerin oy kullanması bekleniyor.
                </small>
            `;
            votingInfoDiv.style.background = 'rgba(253, 219, 58, 0.1)';
            votingInfoDiv.style.borderLeftColor = '#fddb3a';
        }
    }
    
    async completeVoting() {
        if (!this.isHost) {
            this.showNotification('⚠️ Sadece host oylamayı tamamlayabilir!');
            return;
        }
        
        // Get current vote tally and select winner
        try {
            const response = await fetch(`/votes/${this.roomId}/tally`);
            const data = await response.json();
            
            if (!data.tally || data.tally.length === 0) {
                this.showNotification('❌ Henüz oy kullanılmadı!');
                return;
            }
            
            // Force check voting status
            await this.checkVotingStatus();
            
            if (this.votingComplete) {
                this.showNotification('✅ Oylama zaten tamamlandı!');
            } else {
                // In a real scenario, host might manually select winner
                this.showNotification('⚠️ Tüm üyelerin oy vermesi bekleniyor.');
            }
        } catch (error) {
            console.error('Error completing voting:', error);
        }
    }
    
    updateSelectedContent() {
        const selectedContentElement = document.getElementById('selected-content');
        const videoTitleElement = document.getElementById('video-title');
        const movieOverlay = document.getElementById('selected-movie-overlay');
        const movieTitleDisplay = document.getElementById('movie-title-display');
        
        if (this.selectedContent) {
            // Set video duration from selected content
            const durationMin = parseInt(this.selectedContent.duration_min);
            this.duration = durationMin * 60; // Convert minutes to seconds
            
            selectedContentElement.innerHTML = `🏆 <strong style="color: #fddb3a;">${this.selectedContent.title}</strong>`;
            videoTitleElement.innerHTML = `
                <div style="text-align: center;">
                    <div style="font-size: 1.5rem; color: #fddb3a; font-weight: 700;">${this.selectedContent.title}</div>
                    <div style="font-size: 0.9rem; color: #999; margin-top: 0.5rem;">${this.selectedContent.type} • ${this.selectedContent.duration_min} dakika</div>
                    <div style="font-size: 0.8rem; color: #28a745; margin-top: 0.5rem;">✓ ${this.selectedContent.votes} oy ile seçildi</div>
                </div>
            `;
            
            // Show movie title overlay in top-left corner
            if (movieOverlay && movieTitleDisplay) {
                movieTitleDisplay.textContent = this.selectedContent.title;
                movieOverlay.style.display = 'block';
            }
        } else {
            selectedContentElement.textContent = 'Oylama devam ediyor...';
            videoTitleElement.innerHTML = `
                <div style="text-align: center;">
                    <div style="font-size: 1.2rem; color: #fddb3a;">⏳ Oylama Bekleniyor</div>
                    <div style="font-size: 0.9rem; color: #999; margin-top: 0.5rem;">Tüm üyelerin oy kullanması bekleniyor</div>
                </div>
            `;
            
            // Hide movie overlay
            if (movieOverlay) {
                movieOverlay.style.display = 'none';
            }
        }
    }

    // WebSocket Connection
    connectWebSocket() {
        const wsUrl = `ws://localhost:8000/ws/${this.roomId}/${this.userId}`;
        this.websocket = new WebSocket(wsUrl);
        
        // Update health status to connecting
        if (this.updateHealthFromWebSocket) {
            this.updateHealthFromWebSocket('connecting');
        }
        
        this.websocket.onopen = () => {
            console.log('WebSocket connected');
            // Update health status to connected
            if (this.updateHealthFromWebSocket) {
                this.updateHealthFromWebSocket('connected');
            }
        };
        
        this.websocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };
        
        this.websocket.onerror = (error) => {
            console.error('WebSocket error:', error);
            // Update health status to error
            if (this.updateHealthFromWebSocket) {
                this.updateHealthFromWebSocket('error');
            }
        };
        
        this.websocket.onclose = () => {
            console.log('WebSocket disconnected');
            // Update health status to disconnected
            if (this.updateHealthFromWebSocket) {
                this.updateHealthFromWebSocket('disconnected');
            }
            // Reconnect after 3 seconds
            setTimeout(() => this.connectWebSocket(), 3000);
        };
    }

    sendWebSocketEvent(type, data) {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify({ type, ...data }));
        }
    }

    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'chat':
                this.addChatMessage(this.getUserDisplayName(data.user_id), data.message);
                break;
            case 'emoji':
                this.addChatMessage(this.getUserDisplayName(data.user_id), data.emoji);
                break;
            case 'play_pause':
                // Sync play/pause state
                this.isPlaying = data.action === 'play';
                this.currentTime = data.position;
                this.updateProgress();
                break;
            case 'seek':
                // Sync position
                this.currentTime = data.position;
                this.updateProgress();
                break;
            case 'user_joined':
                this.checkRoomStatus();
                const joinedUserName = this.getUserDisplayName(data.user_id);
                this.addChatMessage('Sistem', `${joinedUserName} odaya katıldı 👋`);
                break;
            case 'user_left':
                this.checkRoomStatus();
                const leftUserName = this.getUserDisplayName(data.user_id);
                this.addChatMessage('Sistem', `${leftUserName} odadan ayrıldı 👋`);
                break;
            case 'vote_update':
                this.loadVoteTally();
                this.checkVotingStatus();
                break;
        }
    }
    
    getUserDisplayName(userId) {
        // If it's the current user, show their name
        if (userId === this.userId && this.userData && this.userData.name) {
            return this.userData.name;
        }
        
        // Otherwise, try to extract a readable name from user_id
        // Format: user_abc123 -> User ABC
        if (userId.startsWith('user_')) {
            const suffix = userId.replace('user_', '');
            return `Kullanıcı ${suffix.substring(0, 3).toUpperCase()}`;
        }
        
        // Default: just return the user_id
        return userId;
    }

    // Utility
    startTimer() {
        // Count up timer (elapsed time since session started)
        const countdownElement = document.getElementById('countdown');
        const startTime = Date.now();
        
        setInterval(() => {
            const elapsed = Math.floor((Date.now() - startTime) / 1000);
            
            const hours = Math.floor(elapsed / 3600);
            const minutes = Math.floor((elapsed % 3600) / 60);
            const seconds = elapsed % 60;
            countdownElement.textContent = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }, 1000);
    }

    updateUIWithUserData() {
        // Update header with user info
        const header = document.querySelector('.header-content h1');
        if (header && this.userData) {
            const userAvatar = this.getAvatarEmoji(this.userData.avatar);
            header.innerHTML = `TV+ Sosyal İzleme - ${userAvatar} ${this.userData.name}`;
        }

        // Update room code display
        const roomCodeElement = document.getElementById('room-code');
        if (roomCodeElement && this.roomData) {
            roomCodeElement.textContent = this.roomData.roomId;
        }

        // Update room info
        const selectedContent = document.getElementById('selected-content');
        if (selectedContent && this.roomData) {
            selectedContent.textContent = `Oda: ${this.roomData.roomId}`;
        }

        // Show host status
        if (this.isHost) {
            const roomInfo = document.querySelector('.room-info');
            if (roomInfo) {
                const hostBadge = document.createElement('span');
                hostBadge.textContent = '🎯 Host';
                hostBadge.style.cssText = 'background: linear-gradient(135deg, #ffd700, #ffed4e); color: #1e3c72; padding: 4px 8px; border-radius: 12px; font-size: 0.8rem; font-weight: bold;';
                roomInfo.appendChild(hostBadge);
            }
        }
    }

    getAvatarEmoji(avatar) {
        const avatarMap = {
            'avatar1': '👤',
            'avatar2': '🎭',
            'avatar3': '🎬',
            'avatar4': '🍿',
            'avatar5': '⚽',
            'avatar6': '🎵'
        };
        return avatarMap[avatar] || '👤';
    }

    showNotification(message) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = 'notification';
        notification.textContent = message;
        
        // Determine background color based on message type
        let bgGradient = 'linear-gradient(135deg, #1e3c72, #2a5298)';
        let textColor = 'white';
        
        if (message.includes('✓') || message.includes('eklendi') || message.includes('kaydedildi')) {
            bgGradient = 'linear-gradient(135deg, #28a745, #20c997)';
        } else if (message.includes('❌') || message.includes('⚠️')) {
            bgGradient = 'linear-gradient(135deg, #dc3545, #c82333)';
        } else if (message.includes('💰') || message.includes('🏆')) {
            bgGradient = 'linear-gradient(135deg, #fddb3a, #feca57)';
            textColor = '#1e3c72';
        }
        
        // Style the notification
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 10px;
            color: ${textColor};
            font-weight: 600;
            z-index: 1000;
            background: ${bgGradient};
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
            animation: slideIn 0.3s ease;
            max-width: 300px;
        `;
        
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

    // Party Timer - Counts up from 00:00:00
    startPartyTimer() {
        const updateTimer = () => {
            const elapsed = Math.floor((Date.now() - this.partyStartTime) / 1000);
            const hours = Math.floor(elapsed / 3600);
            const minutes = Math.floor((elapsed % 3600) / 60);
            const seconds = elapsed % 60;
            
            const timerElement = document.getElementById('party-timer');
            if (timerElement) {
                timerElement.textContent = 
                    `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            }
        };
        
        // Update immediately and then every second
        updateTimer();
        setInterval(updateTimer, 1000);
    }

    // Server Health Monitoring
    startHealthMonitoring() {
        const updateHealthUI = (status, text, ping = null) => {
            const healthDot = document.getElementById('health-dot');
            const healthText = document.getElementById('health-text');
            
            if (healthDot) {
                healthDot.className = 'health-dot';
                if (status === 'connecting') {
                    healthDot.classList.add('connecting');
                } else if (status === 'error') {
                    healthDot.classList.add('error');
                }
            }
            
            if (healthText) {
                if (ping !== null) {
                    healthText.textContent = `${text} (${ping}ms)`;
                } else {
                    healthText.textContent = text;
                }
            }
        };
        
        // Check server health via API ping
        const checkHealth = async () => {
            const startTime = Date.now();
            try {
                const response = await fetch('/health');
                const pingTime = Date.now() - startTime;
                this.lastPingTime = pingTime;
                
                if (response.ok) {
                    this.serverHealth = 'connected';
                    updateHealthUI('connected', 'Bağlı', pingTime);
                } else {
                    this.serverHealth = 'error';
                    updateHealthUI('error', 'Hata', pingTime);
                }
            } catch (error) {
                this.serverHealth = 'error';
                updateHealthUI('error', 'Bağlantı Yok');
            }
        };
        
        // Initial check
        updateHealthUI('connecting', 'Bağlanıyor...');
        checkHealth();
        
        // Check every 5 seconds
        setInterval(checkHealth, 5000);
        
        // Also update on WebSocket status
        this.updateHealthFromWebSocket = (status) => {
            if (status === 'connected' && this.serverHealth === 'connected') {
                updateHealthUI('connected', 'Bağlı', this.lastPingTime);
            } else if (status === 'connecting') {
                updateHealthUI('connecting', 'Bağlanıyor...');
            } else if (status === 'disconnected') {
                updateHealthUI('error', 'Bağlantı Kesildi');
            }
        };
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new TVPlusApp();
});
