/**
 * 登录页面JavaScript逻辑
 */

class LoginPage {
    constructor() {
        this.currentTab = 'login';
        this.isLoading = false;
    }

    // 初始化页面
    init() {
        this.bindEvents();
        this.initializeTabs();
    }

    // 绑定事件
    bindEvents() {
        // 标签切换
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', (e) => this.switchTab(e.target.dataset.tab));
        });

        // 表单提交
        document.getElementById('loginForm')?.addEventListener('submit', (e) => this.handleLogin(e));
        document.getElementById('registerForm')?.addEventListener('submit', (e) => this.handleRegister(e));

        // 社交登录
        document.querySelectorAll('.social-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.handleSocialLogin(e));
        });

        // 忘记密码
        document.getElementById('forgotPassword')?.addEventListener('click', (e) => {
            e.preventDefault();
            this.handleForgotPassword();
        });

        // 实时验证
        this.setupFormValidation();
    }

    // 初始化标签
    initializeTabs() {
        this.switchTab('login');
    }

    // 切换标签
    switchTab(tab) {
        this.currentTab = tab;

        // 更新标签按钮状态
        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tab);
        });

        // 更新内容显示
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.toggle('active', content.id === `${tab}Tab`);
        });

        // 清除错误消息
        this.clearMessages();
    }

    // 设置表单验证
    setupFormValidation() {
        // 邮箱格式验证
        document.querySelectorAll('input[type="email"]').forEach(input => {
            input.addEventListener('blur', () => this.validateEmail(input));
            input.addEventListener('input', () => this.clearFieldError(input));
        });

        // 密码强度验证
        document.querySelectorAll('input[type="password"]').forEach(input => {
            if (input.name === 'password' || input.name === 'registerPassword') {
                input.addEventListener('input', () => this.validatePassword(input));
            }
        });

        // 密码确认验证
        const confirmPassword = document.getElementById('confirmPassword');
        if (confirmPassword) {
            confirmPassword.addEventListener('blur', () => this.validatePasswordConfirm());
        }
    }

    // 验证邮箱
    validateEmail(input) {
        const email = input.value.trim();
        if (!email) return;

        if (!Utils.isValidEmail(email)) {
            this.showFieldError(input, '请输入有效的邮箱地址');
            return false;
        }

        this.clearFieldError(input);
        return true;
    }

    // 验证密码
    validatePassword(input) {
        const password = input.value;
        const minLength = 6;

        if (password.length < minLength) {
            this.showFieldError(input, `密码至少需要${minLength}个字符`);
            return false;
        }

        this.clearFieldError(input);
        return true;
    }

    // 验证密码确认
    validatePasswordConfirm() {
        const password = document.getElementById('registerPassword')?.value;
        const confirmPassword = document.getElementById('confirmPassword')?.value;

        if (password !== confirmPassword) {
            this.showFieldError(document.getElementById('confirmPassword'), '两次输入的密码不一致');
            return false;
        }

        this.clearFieldError(document.getElementById('confirmPassword'));
        return true;
    }

    // 显示字段错误
    showFieldError(input, message) {
        input.style.borderColor = '#ef4444';
        
        // 移除已存在的错误提示
        const existingError = input.parentNode.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }

        // 添加新的错误提示
        const errorEl = document.createElement('div');
        errorEl.className = 'field-error text-red-500 text-xs mt-1';
        errorEl.textContent = message;
        input.parentNode.appendChild(errorEl);
    }

    // 清除字段错误
    clearFieldError(input) {
        input.style.borderColor = '';
        const errorEl = input.parentNode.querySelector('.field-error');
        if (errorEl) {
            errorEl.remove();
        }
    }

    // 处理登录
    async handleLogin(e) {
        e.preventDefault();
        
        if (this.isLoading) return;

        const formData = new FormData(e.target);
        const email = formData.get('email')?.trim();
        const password = formData.get('password')?.trim();
        const remember = formData.get('remember') === 'on';

        // 基本验证
        if (!email || !password) {
            this.showError('请填写完整的登录信息');
            return;
        }

        if (!this.validateEmail(document.getElementById('loginEmail'))) {
            return;
        }

        try {
            this.setLoading(true, '登录中...');
            this.clearMessages();

            const response = await ApiClient.post('/users/login', {
                email,
                password
            });

            if (response.success) {
                // 保存认证信息
                Storage.set('auth_token', response.data.token);
                Storage.set('user_info', response.data.userInfo);

                // 记住登录状态
                if (remember) {
                    Storage.set('remember_login', true);
                }

                this.showSuccess('登录成功！正在跳转...');
                
                // 跳转到主页
                setTimeout(() => {
                    window.location.href = 'homepage.html';
                }, 1000);
            }
        } catch (error) {
            console.error('登录失败:', error);
            this.showError(error.message || '登录失败，请检查邮箱和密码');
        } finally {
            this.setLoading(false);
        }
    }

    // 处理注册
    async handleRegister(e) {
        e.preventDefault();
        
        if (this.isLoading) return;

        const formData = new FormData(e.target);
        const name = formData.get('name')?.trim();
        const email = formData.get('email')?.trim();
        const password = formData.get('password')?.trim();
        const confirmPassword = formData.get('confirmPassword')?.trim();
        const birthday = formData.get('birthday');
        const wish = formData.get('wish')?.trim();
        const agreeTerms = formData.get('agreeTerms') === 'on';

        // 验证必填字段
        if (!name || !email || !password || !confirmPassword) {
            this.showError('请填写完整的注册信息');
            return;
        }

        if (!agreeTerms) {
            this.showError('请同意服务条款和隐私政策');
            return;
        }

        // 验证邮箱格式
        if (!this.validateEmail(document.getElementById('registerEmail'))) {
            return;
        }

        // 验证密码
        if (!this.validatePassword(document.getElementById('registerPassword'))) {
            return;
        }

        // 验证密码确认
        if (!this.validatePasswordConfirm()) {
            return;
        }

        try {
            this.setLoading(true, '注册中...');
            this.clearMessages();

            const response = await ApiClient.post('/users/register', {
                name,
                email,
                password,
                birthday,
                wish,
                agreeTerms
            });

            if (response.success) {
                this.showSuccess('注册成功！请登录');
                
                // 切换到登录标签
                setTimeout(() => {
                    this.switchTab('login');
                    // 预填邮箱
                    document.getElementById('loginEmail').value = email;
                }, 1500);
            }
        } catch (error) {
            console.error('注册失败:', error);
            this.showError(error.message || '注册失败，请重试');
        } finally {
            this.setLoading(false);
        }
    }

    // 处理社交登录
    handleSocialLogin(e) {
        e.preventDefault();
        const provider = e.currentTarget.dataset.provider;
        
        Toast.info(`${provider}登录功能开发中...`);
    }

    // 处理忘记密码
    handleForgotPassword() {
        const email = document.getElementById('loginEmail')?.value.trim();
        
        if (!email) {
            Toast.warning('请先输入邮箱地址');
            document.getElementById('loginEmail')?.focus();
            return;
        }

        if (!Utils.isValidEmail(email)) {
            Toast.warning('请输入有效的邮箱地址');
            return;
        }

        Toast.info('忘记密码功能开发中...');
    }

    // 设置加载状态
    setLoading(loading, text = '') {
        this.isLoading = loading;
        
        const submitBtns = document.querySelectorAll('.btn-login');
        submitBtns.forEach(btn => {
            if (loading) {
                btn.disabled = true;
                btn.innerHTML = `<i class="fa fa-spinner fa-spin mr-2"></i>${text}`;
            } else {
                btn.disabled = false;
                btn.innerHTML = this.currentTab === 'login' ? '登录' : '注册';
            }
        });
    }

    // 显示错误消息
    showError(message) {
        this.clearMessages();
        
        const activeTab = document.querySelector('.tab-content.active');
        if (!activeTab) return;

        const errorEl = document.createElement('div');
        errorEl.className = 'error-message';
        errorEl.innerHTML = `<i class="fa fa-exclamation-circle mr-2"></i>${message}`;
        
        activeTab.insertBefore(errorEl, activeTab.firstChild);
    }

    // 显示成功消息
    showSuccess(message) {
        this.clearMessages();
        
        const activeTab = document.querySelector('.tab-content.active');
        if (!activeTab) return;

        const successEl = document.createElement('div');
        successEl.className = 'success-message';
        successEl.innerHTML = `<i class="fa fa-check-circle mr-2"></i>${message}`;
        
        activeTab.insertBefore(successEl, activeTab.firstChild);
    }

    // 清除消息
    clearMessages() {
        document.querySelectorAll('.error-message, .success-message').forEach(el => {
            el.remove();
        });
    }

    // 检查登录状态
    checkLoginStatus() {
        if (Auth.isLoggedIn()) {
            // 如果已经登录，直接跳转到主页
            window.location.href = 'homepage.html';
        }
    }
}

// 创建全局实例
const loginPage = new LoginPage();

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    loginPage.checkLoginStatus();
    loginPage.init();
});

// 导出到全局
window.loginPage = loginPage;