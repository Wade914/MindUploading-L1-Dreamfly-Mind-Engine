// 导航栏组件
class Navbar {
    constructor() {
        this.navbarElement = null;
        this.currentUser = null;
        this.isLoggedIn = false;
    }

    // 初始化导航栏
    init() {
        this.checkLoginStatus();
        this.render();
        this.addEventListeners();
    }

    // 检查登录状态
    checkLoginStatus() {
        // 这里应该从本地存储或API检查登录状态
        const storedUser = localStorage.getItem('currentUser');
        if (storedUser) {
            this.currentUser = JSON.parse(storedUser);
            this.isLoggedIn = true;
        }
    }

    // 渲染导航栏
    render() {
        const navbarContainer = document.getElementById('navbar-container');
        if (!navbarContainer) return;

        // 基础导航栏HTML结构
        let navbarHTML = `
            <header class="sticky top-0 z-50 bg-white shadow-sm">
                <div class="container mx-auto px-4">
                    <div class="flex justify-between items-center py-4">
                        <!-- 左侧Logo -->
                        <div class="flex items-center space-x-4">
                            <a href="square.html" class="text-2xl font-bold text-primary">
                                云己
                                <span class="text-dark">UpMe</span>
                            </a>
                            
                            <!-- 导航菜单 - 桌面端 -->
                            <nav class="hidden md:flex items-center space-x-6">
                                <a href="square.html" class="text-gray-600 hover:text-primary transition-custom">广场</a>
                                <a href="#" class="text-gray-600 hover:text-primary transition-custom">探索</a>
                                <a href="#" class="text-gray-600 hover:text-primary transition-custom">关注</a>
                                <a href="#" class="text-gray-600 hover:text-primary transition-custom">消息</a>
                            </nav>
                        </div>
                        
                        <!-- 右侧工具栏 -->
                        <div class="flex items-center space-x-4">
        `;

        // 搜索框
        navbarHTML += `
                            <!-- 搜索框 -->
                            <div class="relative hidden md:block">
                                <input 
                                    type="text" 
                                    placeholder="搜索思想元胞、用户或话题..." 
                                    class="pl-10 pr-4 py-2 w-64 rounded-full bg-gray-100 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:bg-white transition-custom"
                                    id="navbar-search"
                                >
                                <i class="fa fa-search absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400"></i>
                            </div>
        `;

        // 根据登录状态显示不同内容
        if (this.isLoggedIn && this.currentUser) {
            navbarHTML += `
                                <!-- 发布按钮 -->
                                <button class="bg-primary hover:bg-primary/90 text-white font-medium py-2 px-6 rounded-full flex items-center transition-custom" id="create-post-btn">
                                    <i class="fa fa-pencil-square-o mr-2"></i> 发布
                                </button>
                                
                                <!-- 用户头像 -->
                                <div class="relative" id="user-profile-dropdown">
                                    <button class="w-10 h-10 rounded-full overflow-hidden border-2 border-primary focus:outline-none">
                                        <img 
                                            src="${this.currentUser.avatar || 'https://picsum.photos/seed/user123/200/200'}" 
                                            alt="用户头像" 
                                            class="w-full h-full object-cover"
                                        >
                                    </button>
                                    <!-- 下拉菜单 (默认隐藏) -->
                                    <div class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg py-1 hidden" id="profile-dropdown-menu">
                                        <a href="profile.html" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">个人主页</a>
                                        <a href="#" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">我的收藏</a>
                                        <a href="#" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">设置</a>
                                        <div class="border-t border-gray-200 my-1"></div>
                                        <a href="#" class="block px-4 py-2 text-sm text-red-600 hover:bg-gray-100" id="logout-btn">退出登录</a>
                                    </div>
                                </div>
            `;
        } else {
            navbarHTML += `
                                <!-- 登录/注册按钮 -->
                                <a href="login.html" class="border border-primary text-primary hover:bg-primary/5 font-medium py-2 px-6 rounded-full transition-custom">
                                    登录/注册
                                </a>
            `;
        }

        // 移动端菜单按钮和结束标签
        navbarHTML += `
                                <!-- 移动端菜单按钮 -->
                                <button class="md:hidden text-gray-600 hover:text-primary" id="mobile-menu-btn">
                                    <i class="fa fa-bars text-xl"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                <!-- 移动端菜单 (默认隐藏) -->
                <div class="md:hidden hidden bg-white border-t border-gray-200" id="mobile-menu">
                    <div class="px-4 py-3 space-y-3">
                        <a href="square.html" class="block text-gray-600 hover:text-primary py-2">广场</a>
                        <a href="#" class="block text-gray-600 hover:text-primary py-2">探索</a>
                        <a href="#" class="block text-gray-600 hover:text-primary py-2">关注</a>
                        <a href="#" class="block text-gray-600 hover:text-primary py-2">消息</a>
                        <div class="relative">
                            <input 
                                type="text" 
                                placeholder="搜索..." 
                                class="pl-10 pr-4 py-2 w-full rounded-full bg-gray-100 focus:outline-none"
                            >
                            <i class="fa fa-search absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400"></i>
                        </div>
                    </div>
                </div>
            </header>
        `;

        navbarContainer.innerHTML = navbarHTML;
        this.navbarElement = navbarContainer.querySelector('header');
    }

    // 添加事件监听器
    addEventListeners() {
        // 移动端菜单切换
        const mobileMenuBtn = document.getElementById('mobile-menu-btn');
        const mobileMenu = document.getElementById('mobile-menu');
        
        if (mobileMenuBtn && mobileMenu) {
            mobileMenuBtn.addEventListener('click', () => {
                mobileMenu.classList.toggle('hidden');
            });
        }

        // 用户下拉菜单
        const profileDropdown = document.getElementById('user-profile-dropdown');
        const profileDropdownMenu = document.getElementById('profile-dropdown-menu');
        
        if (profileDropdown && profileDropdownMenu) {
            profileDropdown.addEventListener('click', () => {
                profileDropdownMenu.classList.toggle('hidden');
            });

            // 点击其他地方关闭下拉菜单
            document.addEventListener('click', (e) => {
                if (!profileDropdown.contains(e.target)) {
                    profileDropdownMenu.classList.add('hidden');
                }
            });
        }

        // 退出登录
        const logoutBtn = document.getElementById('logout-btn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.logout();
            });
        }

        // 发布按钮
        const createPostBtn = document.getElementById('create-post-btn');
        if (createPostBtn) {
            createPostBtn.addEventListener('click', () => {
                this.showCreatePostModal();
            });
        }

        // 搜索功能
        const searchInput = document.getElementById('navbar-search');
        if (searchInput) {
            searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.handleSearch(searchInput.value);
                }
            });
        }
    }

    // 处理退出登录
    logout() {
        localStorage.removeItem('currentUser');
        this.isLoggedIn = false;
        this.currentUser = null;
        this.render();
        window.location.href = 'login.html';
    }

    // 显示发布内容模态框
    showCreatePostModal() {
        // 这里应该显示发布内容的模态框
        alert('发布功能暂未实现');
    }

    // 处理搜索
    handleSearch(query) {
        if (query.trim()) {
            // 这里应该处理搜索逻辑
            alert(`搜索: ${query}`);
        }
    }
}

// 导出组件
if (typeof module !== 'undefined') {
    module.exports = Navbar;
} else {
    // 浏览器环境下挂载到全局
    window.Navbar = Navbar;
}