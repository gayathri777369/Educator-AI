/**
 * EducatorAI Frontend JavaScript
 * Handles UI interactions and API communication
 */

class EducatorAI {
    constructor() {
        this.apiBaseUrl = '/api';
        this.currentRequest = null;
        this.initializeEventListeners();
        this.initializeUI();
    }

    /**
     * Initialize event listeners
     */
    initializeEventListeners() {
        // Form submission
        const form = document.getElementById('generateForm');
        form.addEventListener('submit', this.handleFormSubmit.bind(this));

        // Advanced settings toggle
        const toggleBtn = document.getElementById('toggleAdvanced');
        toggleBtn.addEventListener('click', this.toggleAdvancedSettings.bind(this));

        // Range input updates
        const maxLengthInput = document.getElementById('maxLength');
        const temperatureInput = document.getElementById('temperature');
        
        maxLengthInput.addEventListener('input', this.updateRangeValue.bind(this, 'maxLength'));
        temperatureInput.addEventListener('input', this.updateRangeValue.bind(this, 'temperature'));

        // Action buttons
        document.getElementById('copyBtn').addEventListener('click', this.copyToClipboard.bind(this));
        document.getElementById('saveBtn').addEventListener('click', this.saveAsFile.bind(this));
        document.getElementById('retryBtn').addEventListener('click', this.retryGeneration.bind(this));

        // Footer links
        document.getElementById('aboutLink').addEventListener('click', this.showAbout.bind(this));
        document.getElementById('helpLink').addEventListener('click', this.showHelp.bind(this));
    }

    /**
     * Initialize UI components
     */
    initializeUI() {
        // Set initial range values
        this.updateRangeValue('maxLength');
        this.updateRangeValue('temperature');

        // Check API health
        this.checkAPIHealth();
    }

    /**
     * Handle form submission
     */
    async handleFormSubmit(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const requestData = {
            prompt: formData.get('prompt'),
            content_type: formData.get('contentType'),
            context: formData.get('context') || null,
            max_length: parseInt(formData.get('maxLength')),
            temperature: parseFloat(formData.get('temperature'))
        };

        // Validate form
        if (!this.validateForm(requestData)) {
            return;
        }

        // Store current request for retry
        this.currentRequest = requestData;

        // Start generation
        await this.generateContent(requestData);
    }

    /**
     * Validate form data
     */
    validateForm(data) {
        if (!data.prompt || data.prompt.trim().length === 0) {
            this.showError('Please enter a topic or question.');
            return false;
        }

        if (data.prompt.length > 1000) {
            this.showError('Prompt is too long. Please limit to 1000 characters.');
            return false;
        }

        if (data.context && data.context.length > 2000) {
            this.showError('Context is too long. Please limit to 2000 characters.');
            return false;
        }

        return true;
    }

    /**
     * Generate content via API
     */
    async generateContent(requestData) {
        try {
            // Show loading state
            this.showLoadingState();

            // Make API request
            const response = await fetch(`${this.apiBaseUrl}/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });

            const result = await response.json();

            if (result.success) {
                this.showResult(result);
            } else {
                this.showError(result.error || 'Failed to generate content');
            }

        } catch (error) {
            console.error('Error generating content:', error);
            this.showError('Network error. Please check your connection and try again.');
        }
    }

    /**
     * Show loading state
     */
    showLoadingState() {
        this.hideAllStates();
        document.getElementById('loadingState').classList.remove('hidden');
        
        // Disable form
        const submitBtn = document.getElementById('generateBtn');
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
    }

    /**
     * Show result
     */
    showResult(result) {
        this.hideAllStates();
        
        const resultContainer = document.getElementById('resultContainer');
        const generatedText = document.getElementById('generatedText');
        const resultType = document.getElementById('resultType');
        const resultTime = document.getElementById('resultTime');

        // Set content
        generatedText.textContent = result.generated_text;
        resultType.textContent = result.content_type;
        resultTime.textContent = `Generated in ${result.processing_time?.toFixed(2)}s`;

        // Show result
        resultContainer.classList.remove('hidden');

        // Re-enable form
        this.resetForm();
    }

    /**
     * Show error state
     */
    showError(message) {
        this.hideAllStates();
        
        const errorState = document.getElementById('errorState');
        const errorMessage = document.getElementById('errorMessage');
        
        errorMessage.textContent = message;
        errorState.classList.remove('hidden');

        // Re-enable form
        this.resetForm();
    }

    /**
     * Hide all states
     */
    hideAllStates() {
        document.getElementById('loadingState').classList.add('hidden');
        document.getElementById('emptyState').classList.add('hidden');
        document.getElementById('resultContainer').classList.add('hidden');
        document.getElementById('errorState').classList.add('hidden');
    }

    /**
     * Reset form to initial state
     */
    resetForm() {
        const submitBtn = document.getElementById('generateBtn');
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-magic"></i> <span>Generate Content</span>';
    }

    /**
     * Toggle advanced settings
     */
    toggleAdvancedSettings() {
        const toggleBtn = document.getElementById('toggleAdvanced');
        const panel = document.getElementById('advancedPanel');
        
        toggleBtn.classList.toggle('active');
        panel.classList.toggle('open');
    }

    /**
     * Update range input value display
     */
    updateRangeValue(inputId) {
        const input = document.getElementById(inputId);
        const valueSpan = document.getElementById(`${inputId}Value`);
        valueSpan.textContent = input.value;
    }

    /**
     * Copy content to clipboard
     */
    async copyToClipboard() {
        const generatedText = document.getElementById('generatedText');
        
        try {
            await navigator.clipboard.writeText(generatedText.textContent);
            this.showToast('Content copied to clipboard!');
        } catch (error) {
            console.error('Failed to copy:', error);
            this.showToast('Failed to copy content', 'error');
        }
    }

    /**
     * Save content as file
     */
    saveAsFile() {
        const generatedText = document.getElementById('generatedText');
        const contentType = document.getElementById('resultType').textContent;
        
        const blob = new Blob([generatedText.textContent], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `educatorai-${contentType}-${Date.now()}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.showToast('Content saved as file!');
    }

    /**
     * Retry generation with last request
     */
    async retryGeneration() {
        if (this.currentRequest) {
            await this.generateContent(this.currentRequest);
        }
    }

    /**
     * Show toast notification
     */
    showToast(message, type = 'success') {
        const toast = document.getElementById('toast');
        const toastMessage = document.getElementById('toastMessage');
        const toastIcon = toast.querySelector('i');
        
        toastMessage.textContent = message;
        
        // Set icon based on type
        if (type === 'error') {
            toastIcon.className = 'fas fa-exclamation-circle';
            toast.style.backgroundColor = 'var(--error-color)';
        } else {
            toastIcon.className = 'fas fa-check-circle';
            toast.style.backgroundColor = 'var(--success-color)';
        }
        
        toast.classList.add('show');
        
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }

    /**
     * Check API health
     */
    async checkAPIHealth() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/health`);
            const health = await response.json();
            
            if (!health.model_loaded) {
                this.showError('AI model is loading. Please wait a moment and try again.');
            }
        } catch (error) {
            console.error('Health check failed:', error);
            this.showError('Unable to connect to AI service. Please refresh the page.');
        }
    }

    /**
     * Show about dialog
     */
    showAbout(event) {
        event.preventDefault();
        alert(`EducatorAI v1.0.0

An educational AI application powered by IBM Granite 3.3-2b-instruct model.

Features:
- Generate educational content
- Multiple content types
- Customizable parameters
- Export and copy functionality

Built with FastAPI and Hugging Face Transformers.`);
    }

    /**
     * Show help dialog
     */
    showHelp(event) {
        event.preventDefault();
        alert(`How to use EducatorAI:

1. Select a content type (explanation, summary, quiz, etc.)
2. Enter your educational topic or question
3. Optionally add context for better results
4. Adjust advanced settings if needed
5. Click "Generate Content" to create educational material

Tips:
- Be specific with your prompts
- Use context to specify target audience
- Experiment with different content types
- Save or copy generated content for later use`);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new EducatorAI();
});

// Handle browser back/forward navigation
window.addEventListener('popstate', () => {
    location.reload();
});