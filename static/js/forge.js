// Forge interface JavaScript functionality
class ForgeInterface {
    constructor() {
        this.sessionId = null;
        this.considerations = {};
        this.chatHistory = [];
        this.isTyping = false;
        this.pendingUpdates = new Set(); // Track which considerations are being updated
        
        this.initializeElements();
        this.bindEvents();
        this.loadSessionStatus();
        this.initializeConsiderations();
    }
    
    initializeElements() {
        this.chatContainer = document.getElementById('chatContainer');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.progressBar = document.getElementById('progressBar');
        this.progressText = document.getElementById('progressText');
        this.submitBtn = document.getElementById('submitBtn');
        this.confirmSubmit = document.getElementById('confirmSubmit');
        this.submitModal = new bootstrap.Modal(document.getElementById('submitModal'));
    }
    
    bindEvents() {
        // Chat functionality
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Edit functionality
        document.querySelectorAll('.edit-consideration').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const considerationId = e.target.dataset.considerationId;
                this.enterEditMode(considerationId);
            });
        });
        
        // Save functionality
        document.querySelectorAll('.save-consideration').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const considerationId = e.target.dataset.considerationId;
                this.saveConsideration(considerationId);
            });
        });
        
        // Cancel edit functionality
        document.querySelectorAll('.cancel-edit').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const considerationId = e.target.dataset.considerationId;
                this.cancelEditMode(considerationId);
            });
        });
        
        // Auto-save on textarea change in edit mode
        document.querySelectorAll('.consideration-textarea').forEach(textarea => {
            textarea.addEventListener('input', (e) => {
                this.updateWordCount(e.target);
            });
        });
        
        // Submit functionality
        this.submitBtn.addEventListener('click', () => this.submitModal.show());
        this.confirmSubmit.addEventListener('click', () => this.submitIdea());
    }
    
    initializeConsiderations() {
        // Initialize all consideration boxes
        document.querySelectorAll('.consideration-box').forEach(box => {
            const considerationId = box.dataset.considerationId;
            const textElement = box.querySelector('.consideration-text');
            const content = textElement.textContent.trim();
            
            // Check if it's placeholder text
            if (content === 'Will be filled by AI...') {
                textElement.classList.add('placeholder');
            } else if (content) {
                this.updateConsiderationStatus(considerationId, content);
            }
        });
        this.updateProgress();
    }
    
    async loadSessionStatus() {
        try {
            const response = await fetch('/api/session_status');
            const data = await response.json();
            
            if (data.session_id) {
                this.sessionId = data.session_id;
                this.updateProgress(data.completion_status);
                this.submitBtn.disabled = !data.can_submit;
            }
        } catch (error) {
            console.error('Error loading session status:', error);
        }
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || this.isTyping) return;
        
        this.isTyping = true;
        this.messageInput.value = '';
        this.sendBtn.disabled = true;
        this.typingIndicator.style.display = 'block';
        
        // Add user message to chat
        this.addMessageToChat(message, 'user');
        
        // Mark some considerations as updating if this seems like substantial input
        if (message.length > 50) {
            this.simulateAIConsiderationUpdates();
        }
        
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });
            
            const data = await response.json();
            
            if (data.response) {
                this.addMessageToChat(data.response, 'assistant');
                this.sessionId = data.session_id;
                
                // Simulate AI updating considerations
                await this.processAIConsiderationUpdates(data.response);
            } else {
                throw new Error(data.error || 'Failed to get response');
            }
        } catch (error) {
            console.error('Error sending message:', error);
            this.addMessageToChat('Sorry, I encountered an error. Please try again.', 'assistant');
        } finally {
            this.isTyping = false;
            this.sendBtn.disabled = false;
            this.typingIndicator.style.display = 'none';
        }
    }
    
    addMessageToChat(message, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        messageDiv.innerHTML = `<strong>${sender === 'user' ? 'You' : 'ASF'}:</strong> ${message}`;
        
        this.chatContainer.appendChild(messageDiv);
        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
    }
    
    updateWordCount(textarea) {
        const words = textarea.value.trim().split(/\s+/).filter(word => word.length > 0).length;
        const wordCountElement = textarea.parentElement.querySelector('.current-words');
        if (wordCountElement) {
            wordCountElement.textContent = words;
        }
    }
    
    updateConsiderationStatus(considerationId, content) {
        const words = content.trim().split(/\s+/).filter(word => word.length > 0).length;
        const box = document.querySelector(`[data-consideration-id="${considerationId}"]`);
        const statusIcon = box.querySelector('.consideration-status i');
        
        if (words >= 100) {
            box.classList.add('completed');
            box.classList.remove('in-progress', 'updating');
            statusIcon.className = 'bi bi-check-circle text-success';
        } else if (words > 0) {
            box.classList.add('in-progress');
            box.classList.remove('completed', 'updating');
            statusIcon.className = 'bi bi-clock text-warning';
        } else {
            box.classList.remove('completed', 'in-progress', 'updating');
            statusIcon.className = 'bi bi-circle text-muted';
        }
    }
    
    simulateAIConsiderationUpdates() {
        // Mark 2-3 random considerations as updating
        const considerations = Array.from(document.querySelectorAll('.consideration-box'));
        const toUpdate = considerations
            .filter(box => !box.classList.contains('completed'))
            .slice(0, Math.floor(Math.random() * 3) + 1);
            
        toUpdate.forEach(box => {
            box.classList.add('updating');
            this.pendingUpdates.add(box.dataset.considerationId);
        });
    }
    
    async processAIConsiderationUpdates(aiResponse) {
        // Simulate AI extracting information to fill considerations
        // In a real implementation, the AI would return structured data
        
        // For now, simulate by updating random pending considerations
        const pendingArray = Array.from(this.pendingUpdates);
        
        for (const considerationId of pendingArray) {
            // Simulate delay
            await new Promise(resolve => setTimeout(resolve, 500 + Math.random() * 1000));
            
            // Generate relevant content based on consideration type
            const content = this.generateSampleContent(considerationId, aiResponse);
            
            if (content) {
                await this.updateConsiderationContent(considerationId, content);
            }
            
            this.pendingUpdates.delete(considerationId);
        }
    }
    
    generateSampleContent(considerationId, aiResponse) {
        // This would normally be extracted from AI response
        // For now, generate relevant placeholder content
        const templates = {
            'problem_definition': `Based on our conversation, the core problem appears to be [extracted from chat]. This represents a significant market opportunity because [reasoning]. The problem affects [target users] and currently costs them [impact].`,
            'target_market': `The primary target market consists of [market segment] with an estimated size of [market size]. Key demographics include [user characteristics]. The market is currently served by [existing solutions] but shows clear gaps in [specific areas].`,
            'solution_approach': `Our proposed solution involves [solution description]. The key innovation is [unique approach] which addresses the problem by [mechanism]. This approach is differentiated because [competitive advantage].`,
            'competitive_analysis': `Current market players include [competitors]. Our competitive advantage lies in [differentiation]. Market gaps we can exploit: [opportunities]. Competitive risks: [threats] which we mitigate by [strategies].`,
            'business_model': `Revenue generation through [revenue streams]. Primary monetization: [main revenue]. Pricing strategy: [pricing approach]. Customer acquisition cost estimated at [CAC] with lifetime value of [LTV].`,
            'technical_feasibility': `Technical implementation requires [tech stack]. Key technical challenges: [challenges] with solutions: [solutions]. Development timeline: [timeline]. Required expertise: [skills needed].`,
            'team_structure': `Core team roles needed: [roles]. Key hires: [critical positions]. Equity distribution: [equity plan]. Advisory board should include [advisor types]. Team formation strategy: [hiring plan].`,
            'growth_strategy': `Go-to-market strategy: [GTM]. Customer acquisition channels: [channels]. Growth milestones: [milestones]. Scaling plan: [scaling strategy]. Key metrics to track: [KPIs].`
        };
        
        return templates[considerationId] || `[AI-generated content for ${considerationId} based on conversation]`;
    }
    
    async updateConsiderationContent(considerationId, content) {
        const box = document.querySelector(`[data-consideration-id="${considerationId}"]`);
        const textElement = box.querySelector('.consideration-text');
        
        // Remove placeholder styling
        textElement.classList.remove('placeholder');
        
        // Animate text update
        textElement.style.opacity = '0.5';
        
        setTimeout(() => {
            textElement.textContent = content;
            textElement.style.opacity = '1';
            
            // Update status
            this.updateConsiderationStatus(considerationId, content);
            
            // Save to backend
            this.saveConsiderationSilently(considerationId, content);
            
            // Update progress
            this.updateProgress();
        }, 300);
    }
    
    enterEditMode(considerationId) {
        const box = document.querySelector(`[data-consideration-id="${considerationId}"]`);
        const textDiv = box.querySelector('.consideration-text');
        const editDiv = box.querySelector('.consideration-edit');
        const textarea = box.querySelector('.consideration-textarea');
        const editBtn = box.querySelector('.edit-consideration');
        
        // Set textarea value to current text content
        textarea.value = textDiv.textContent.trim();
        if (textarea.value === 'Will be filled by AI...') {
            textarea.value = '';
        }
        
        // Switch views
        textDiv.style.display = 'none';
        editDiv.classList.remove('d-none');
        editBtn.style.display = 'none';
        
        // Focus textarea
        textarea.focus();
        
        // Update word count
        this.updateWordCount(textarea);
    }
    
    cancelEditMode(considerationId) {
        const box = document.querySelector(`[data-consideration-id="${considerationId}"]`);
        const textDiv = box.querySelector('.consideration-text');
        const editDiv = box.querySelector('.consideration-edit');
        const editBtn = box.querySelector('.edit-consideration');
        
        // Switch views back
        textDiv.style.display = 'block';
        editDiv.classList.add('d-none');
        editBtn.style.display = 'inline-block';
    }
    
    async saveConsideration(considerationId) {
        const box = document.querySelector(`[data-consideration-id="${considerationId}"]`);
        const textDiv = box.querySelector('.consideration-text');
        const editDiv = box.querySelector('.consideration-edit');
        const textarea = box.querySelector('.consideration-textarea');
        const editBtn = box.querySelector('.edit-consideration');
        const content = textarea.value.trim();
        
        try {
            const response = await fetch('/api/update_consideration', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    consideration_id: considerationId,
                    content: content
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Update the text display
                if (content) {
                    textDiv.textContent = content;
                    textDiv.classList.remove('placeholder');
                } else {
                    textDiv.textContent = 'Will be filled by AI...';
                    textDiv.classList.add('placeholder');
                }
                
                // Update status and progress
                this.updateConsiderationStatus(considerationId, content);
                this.updateProgress(data.completion_status);
                this.submitBtn.disabled = !data.completion_status.can_submit;
                
                // Exit edit mode
                this.cancelEditMode(considerationId);
                
                // Show save confirmation
                const saveBtn = box.querySelector('.save-consideration');
                const originalText = saveBtn.innerHTML;
                saveBtn.innerHTML = '<i class="bi bi-check me-1"></i>Saved';
                saveBtn.classList.add('btn-success');
                saveBtn.classList.remove('btn-outline-primary');
                
                setTimeout(() => {
                    saveBtn.innerHTML = originalText;
                    saveBtn.classList.remove('btn-success');
                    saveBtn.classList.add('btn-outline-primary');
                }, 2000);
            }
        } catch (error) {
            console.error('Error saving consideration:', error);
        }
    }
    
    async saveConsiderationSilently(considerationId, content) {
        // Save without UI feedback (used by AI updates)
        try {
            await fetch('/api/update_consideration', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    consideration_id: considerationId,
                    content: content
                })
            });
        } catch (error) {
            console.error('Error saving consideration silently:', error);
        }
    }
    
    updateProgress(completionStatus = null) {
        if (!completionStatus) {
            // Calculate from DOM
            const completedCount = document.querySelectorAll('.consideration-box.completed').length;
            completionStatus = {
                completed_count: completedCount,
                total_count: 8,
                can_submit: completedCount >= 6
            };
        }
        
        const percentage = (completionStatus.completed_count / completionStatus.total_count) * 100;
        this.progressBar.style.width = `${percentage}%`;
        this.progressText.textContent = `${completionStatus.completed_count}/${completionStatus.total_count} Developed`;
        
        // Update progress bar color
        this.progressBar.className = 'progress-bar';
        if (percentage >= 75) {
            this.progressBar.classList.add('bg-success');
        } else if (percentage >= 50) {
            this.progressBar.classList.add('bg-warning');
        } else {
            this.progressBar.classList.add('bg-info');
        }
        
        // Update submit button state
        this.submitBtn.disabled = !completionStatus.can_submit;
    }
    
    async submitIdea() {
        try {
            const response = await fetch('/api/submit_idea', {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.submitModal.hide();
                
                // Show success message
                const alert = document.createElement('div');
                alert.className = 'alert alert-success alert-dismissible fade show';
                alert.innerHTML = `
                    <i class="bi bi-check-circle me-2"></i>
                    ${data.message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                `;
                
                document.querySelector('.container').insertBefore(alert, document.querySelector('.row'));
                
                // Disable submit button
                this.submitBtn.disabled = true;
                this.submitBtn.innerHTML = '<i class="bi bi-check me-1"></i>Submitted';
                
                // Auto-redirect to marketplace after 3 seconds
                setTimeout(() => {
                    window.location.href = `/idea/${data.idea_id}`;
                }, 3000);
                
            } else {
                throw new Error(data.error || 'Failed to submit idea');
            }
        } catch (error) {
            console.error('Error submitting idea:', error);
            alert('Error submitting idea: ' + error.message);
        }
    }
    
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Initialize the forge interface when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    new ForgeInterface();
});
