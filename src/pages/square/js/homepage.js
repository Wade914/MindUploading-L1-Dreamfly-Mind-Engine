/**
 * 个人主页JavaScript逻辑
 */

class Homepage {
    constructor() {
        this.currentUser = null;
        this.thoughtCells = [];
        this.isLoading = false;
    }

    // 初始化页面
    async init() {
        this.bindEvents();
        await this.loadUserData();
        await this.loadUserThoughtCells();
        this.initializeComponents();
    }

    // 绑定事件
    bindEvents() {
        // 编辑资料按钮
        document.getElementById('editProfileBtn')?.addEventListener('click', () => this.openEditModal());
        
        // 发布思想元胞
        document.getElementById('publishThoughtBtn')?.addEventListener('click', () => this.publishThought());
        
        // 登出按钮
        document.getElementById('logoutBtn')?.addEventListener('click', () => this.logout());
        
        // 分享按钮
        document.getElementById('shareBtn')?.addEventListener('click', () => this.shareProfile());
        
        // MindOS按钮
        document.getElementById('mindOSBtn')?.addEventListener('click', () => {
            window.location.href = 'mindos.html';
        });

        // 发布工具按钮
        document.getElementById('uploadImageBtn')?.addEventListener('click', () => this.toggleImageUpload());
        document.getElementById('addQuoteBtn')?.addEventListener('click', () => this.toggleQuoteArea());
        document.getElementById('addTagsBtn')?.addEventListener('click', () => this.toggleTagsArea());

        // 创建测试数据按钮
        document.getElementById('createTestThoughtBtn')?.addEventListener('click', () => this.createTestThoughts());
    }

    // 加载用户数据
    async loadUserData() {
        try {
            Loading.show('#main-content', '加载个人资料...');

            // 从 Auth 获取用户信息 (从 token 解析)
            this.currentUser = Auth.getCurrentUser();

            if (!this.currentUser) {
                Toast.error('请先登录');
                setTimeout(() => {
                    window.location.href = 'login.html';
                }, 1000);
                return;
            }

            // 尝试从后端 API 获取完整的用户资料 (包括统计数据)
            if (Auth.isLoggedIn()) {
                try {
                    const response = await ApiClient.get(`/api/square/users/${this.currentUser.user_id}`);
                    if (response.code === 200 && response.data && response.data.profile) {
                        // 合并用户信息 (保留 token 中的基本信息,添加 API 返回的扩展信息)
                        this.currentUser = {
                            ...this.currentUser,
                            avatar_url: response.data.profile.avatar_url,
                            bio: response.data.profile.bio,
                            location: response.data.profile.location,
                            website: response.data.profile.website,
                            stats: {
                                thoughts_count: response.data.profile.thoughts_count,
                                following_count: response.data.profile.following_count,
                                followers_count: response.data.profile.followers_count
                            }
                        };
                    }
                } catch (error) {
                    console.warn('从 API 获取用户资料失败,使用基本信息:', error);
                    // 使用默认的统计数据
                    this.currentUser.stats = {
                        thoughts_count: 0,
                        following_count: 0,
                        followers_count: 0
                    };
                }
            }

            this.updateUserProfile();

        } catch (error) {
            console.error('加载用户数据失败:', error);
            Toast.error('加载个人资料失败');
        } finally {
            Loading.hide('#main-content');
        }
    }

    // 格式化用户数据
    formatUserData(backendData) {
        const user = backendData.user || backendData;
        return {
            user_id: user.user_id,
            username: user.username,
            avatar: user.avatar || 'https://picsum.photos/seed/default/400/400',
            bio: user.bio || '',
            email: user.email || '',
            location: user.location || '',
            occupation: user.occupation || '',
            birthdate: user.birthdate || '1990-01-01',
            coverGradient: user.coverGradient || 'from-blue-700 to-purple-800',
            milestones: backendData.milestones || [],
            stats: {
                thoughtCount: user.stats?.thought_cells_count || 0,
                followingCount: user.stats?.following_count || 0,
                followerCount: user.stats?.followers_count || 1
            }
        };
    }

    // 获取默认用户数据
    getDefaultUserData() {
        return {
            user_id: 'default_user',
            username: '云己用户',
            avatar: 'https://picsum.photos/seed/default/400/400',
            bio: '欢迎来到我的个人主页',
            email: 'user@example.com',
            location: '北京市',
            occupation: '数字生命探索者',
            birthdate: '1990-01-01',
            coverGradient: 'from-blue-700 to-purple-800',
            milestones: [
                { year: '1990', event: '出生' },
                { year: '2024', event: '开始探索数字生命的意义' }
            ],
            stats: {
                thoughtCount: 0,
                followingCount: 0,
                followerCount: 1
            }
        };
    }

    // 更新用户资料显示
    updateUserProfile() {
        if (!this.currentUser) return;

        // 更新基本信息
        this.updateElement('userName', this.currentUser.username);
        this.updateElement('userBio', this.currentUser.bio);
        this.updateElement('profileAvatar', this.currentUser.avatar, 'src');
        this.updateElement('postAvatar', this.currentUser.avatar, 'src');
        
        // 更新个人信息卡片
        this.updateElement('infoName', this.currentUser.username);
        this.updateElement('infoEmail', this.currentUser.email);
        this.updateElement('infoLocation', this.currentUser.location);
        this.updateElement('infoOccupation', this.currentUser.occupation);
        this.updateElement('infoBirthdate', this.currentUser.birthdate);
        
        // 应用封面色调
        this.applyCoverGradient(this.currentUser.coverGradient);
        
        // 更新生命天数
        this.updateLifeDayCount(this.currentUser.birthdate);
        this.updateElement('birthDate', this.currentUser.birthdate);
        
        // 更新统计数据
        this.updateUserStats();
        
        // 更新里程碑
        this.updateMilestones(this.currentUser.milestones);
    }

    // 更新元素内容
    updateElement(id, value, attribute = 'textContent') {
        const element = document.getElementById(id);
        if (element && value !== undefined) {
            if (attribute === 'textContent') {
                element.textContent = value;
            } else {
                element[attribute] = value;
            }
        }
    }

    // 应用封面色调
    applyCoverGradient(gradient) {
        const profileHeader = document.querySelector('section.bg-gradient-to-r');
        if (profileHeader && gradient) {
            profileHeader.className = `bg-gradient-to-r ${gradient} text-white`;
        }
    }

    // 更新生命天数
    updateLifeDayCount(birthdate) {
        const lifeDays = Utils.calculateLifeDays(birthdate);
        this.updateElement('lifeDayCount', lifeDays);
    }

    // 更新用户统计
    updateUserStats() {
        if (this.currentUser?.stats) {
            this.updateElement('thoughtCount', this.currentUser.stats.thoughts_count || 0);
            this.updateElement('followingCount', this.currentUser.stats.following_count || 0);
            this.updateElement('followerCount', this.currentUser.stats.followers_count || 0);
        }
    }

    // 更新里程碑
    updateMilestones(milestones) {
        const container = document.getElementById('milestones');
        if (!container || !Array.isArray(milestones)) return;
        
        container.innerHTML = '';
        
        milestones.forEach((milestone, index) => {
            const milestoneElement = document.createElement('div');
            milestoneElement.className = 'milestone-item';
            milestoneElement.innerHTML = `
                <div class="flex items-start space-x-4">
                    <div class="flex-shrink-0 w-16 text-right">
                        <span class="text-lg font-bold text-blue-600">${milestone.year}</span>
                    </div>
                    <div class="flex-1">
                        <p class="text-gray-700">${milestone.event}</p>
                    </div>
                </div>
            `;
            container.appendChild(milestoneElement);
        });
    }

    // 加载思想元胞
    async loadUserThoughtCells() {
        try {
            // 先从本地存储获取
            this.thoughtCells = Storage.get('thought_cells', []);
            this.renderThoughtCells();
            
            // 然后尝试从API获取最新数据
            if (Auth.isLoggedIn()) {
                const response = await ApiClient.get('/api/square/thoughts');
                if (response.code === 200 && response.data?.thoughts) {
                    this.thoughtCells = response.data.thoughts;
                    Storage.set('thought_cells', this.thoughtCells);
                    this.renderThoughtCells();
                }
            }
        } catch (error) {
            console.error('加载思想元胞失败:', error);
            this.renderThoughtCells();
        }
    }

    // 渲染思想元胞
    renderThoughtCells() {
        const container = document.getElementById('thoughtsContainer');
        const emptyCard = document.getElementById('emptyThoughtsCard');
        
        if (!container) return;
        
        container.innerHTML = '';
        
        if (this.thoughtCells.length === 0) {
            emptyCard?.classList.remove('hidden');
            return;
        }
        
        emptyCard?.classList.add('hidden');
        
        this.thoughtCells.forEach(thought => {
            this.addThoughtCellToPage(thought);
        });
    }

    // 添加思想元胞到页面
    addThoughtCellToPage(thoughtCell) {
        const container = document.getElementById('thoughtsContainer');
        if (!container) return;
        
        const thoughtElement = document.createElement('div');
        thoughtElement.className = 'thought-cell';
        thoughtElement.setAttribute('data-thought-id', thoughtCell.id);
        
        // 计算生命纪年
        const lifeYear = Utils.calculateLifeYear(this.currentUser.birthdate, thoughtCell.createdAt);
        const formattedDate = Utils.formatDate(thoughtCell.createdAt);
        
        thoughtElement.innerHTML = `
            <div class="thought-cell-header">
                <div class="flex items-start space-x-4">
                    <img src="${thoughtCell.avatar || this.currentUser.avatar}" alt="用户头像" class="avatar avatar-md">
                    <div class="flex-1">
                        <div class="flex justify-between items-start">
                            <div>
                                <h4 class="font-bold text-gray-800">${thoughtCell.username || this.currentUser.username}</h4>
                                <div class="flex items-center space-x-2 text-xs text-gray-500 mt-1">
                                    <span class="bg-gradient-to-r from-blue-500 to-purple-500 text-white px-2 py-1 rounded-full font-medium">
                                        生命第 ${lifeYear.day} 天
                                    </span>
                                    <span class="text-gray-400">•</span>
                                    <span class="hover:text-gray-700 cursor-pointer" title="${formattedDate}">
                                        ${lifeYear.year}年${lifeYear.month}月
                                    </span>
                                </div>
                            </div>
                            <div class="flex space-x-2">
                                <button class="text-gray-400 hover:text-blue-500 transition-colors p-1 rounded-full hover:bg-blue-50" onclick="homepage.editThought('${thoughtCell.id}')" title="编辑">
                                    <i class="fa fa-pencil"></i>
                                </button>
                                <button class="text-gray-400 hover:text-red-500 transition-colors p-1 rounded-full hover:bg-red-50" onclick="homepage.deleteThought('${thoughtCell.id}')" title="删除">
                                    <i class="fa fa-trash"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="thought-cell-content">
                <div class="text-gray-800 leading-relaxed whitespace-pre-line">
                    ${thoughtCell.content}
                </div>
                
                ${thoughtCell.quote ? `
                    <div class="thought-quote mt-4">
                        ${thoughtCell.quote}
                    </div>
                ` : ''}
                
                ${thoughtCell.images && thoughtCell.images.length > 0 ? `
                    <div class="mt-4 grid grid-cols-1 md:grid-cols-2 gap-3">
                        ${thoughtCell.images.map((img, index) => `
                            <img src="${img}" alt="思想图片 ${index + 1}" class="w-full h-48 object-cover rounded-lg cursor-pointer" onclick="homepage.openImageModal('${img}')">
                        `).join('')}
                    </div>
                ` : ''}
                
                ${thoughtCell.tags && thoughtCell.tags.length > 0 ? `
                    <div class="mt-4 flex flex-wrap gap-2">
                        ${thoughtCell.tags.map(tag => `
                            <span class="tag">#${tag}</span>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
            
            <div class="thought-cell-footer">
                <div class="thought-actions">
                    <button class="thought-action-btn ${thoughtCell.isLiked ? 'active' : ''}" onclick="homepage.toggleLike('${thoughtCell.id}')">
                        <i class="fa fa-heart${thoughtCell.isLiked ? '' : '-o'}"></i>
                        <span>${thoughtCell.likesCount || 0}</span>
                    </button>
                    <button class="thought-action-btn" onclick="homepage.commentThought('${thoughtCell.id}')">
                        <i class="fa fa-comment-o"></i>
                        <span>${thoughtCell.commentsCount || 0}</span>
                    </button>
                    <button class="thought-action-btn" onclick="homepage.shareThought('${thoughtCell.id}')">
                        <i class="fa fa-share-alt"></i>
                        <span>分享</span>
                    </button>
                    <button class="thought-action-btn ${thoughtCell.isSaved ? 'active' : ''}" onclick="homepage.toggleSave('${thoughtCell.id}')">
                        <i class="fa fa-bookmark${thoughtCell.isSaved ? '' : '-o'}"></i>
                        <span>${thoughtCell.isSaved ? '已收藏' : '收藏'}</span>
                    </button>
                </div>
            </div>
        `;
        
        container.appendChild(thoughtElement);
    }

    // 发布思想元胞
    async publishThought() {
        const content = document.getElementById('thoughtContent')?.value.trim();
        const quote = document.getElementById('thoughtQuote')?.value.trim();
        const tags = document.getElementById('thoughtTags')?.value.trim();
        
        if (!content) {
            Toast.warning('请输入思想元胞内容');
            return;
        }

        if (!Auth.requireAuth()) return;

        try {
            Loading.show('#publishThoughtBtn', '发布中...');
            
            // 处理图片
            const imageFiles = document.getElementById('thoughtImageInput')?.files || [];
            
            // 创建FormData
            const formData = new FormData();
            formData.append('content', content);
            if (quote) formData.append('quote', quote);
            if (tags) formData.append('tags', tags);
            formData.append('visibility', 'public');
            
            // 添加图片文件
            for (let i = 0; i < imageFiles.length; i++) {
                formData.append('files', imageFiles[i]);
            }
            
            const response = await ApiClient.upload('/api/square/thoughts', formData);
            
            if (response.code === 200) {
                // 清空表单
                this.clearPublishForm();
                
                // 重新加载思想元胞
                await this.loadUserThoughtCells();
                
                // 更新统计
                if (this.currentUser?.stats) {
                    this.currentUser.stats.thoughts_count++;
                    this.updateUserStats();
                }
                
                Toast.success('思想元胞发布成功！');
            }
        } catch (error) {
            console.error('发布失败:', error);
            Toast.error('发布失败: ' + error.message);
        } finally {
            Loading.hide('#publishThoughtBtn');
        }
    }

    // 清空发布表单
    clearPublishForm() {
        const elements = [
            'thoughtContent',
            'thoughtQuote', 
            'thoughtTags',
            'thoughtImageInput'
        ];
        
        elements.forEach(id => {
            const element = document.getElementById(id);
            if (element) element.value = '';
        });
        
        // 隐藏可选区域
        document.getElementById('imageUploadArea')?.classList.add('hidden');
        document.getElementById('quoteArea')?.classList.add('hidden');
        document.getElementById('tagsArea')?.classList.add('hidden');
        
        // 清空图片预览
        const previewContainer = document.getElementById('previewImages');
        if (previewContainer) previewContainer.innerHTML = '';
    }

    // 切换图片上传区域
    toggleImageUpload() {
        const area = document.getElementById('imageUploadArea');
        area?.classList.toggle('hidden');
    }

    // 切换引用区域
    toggleQuoteArea() {
        const area = document.getElementById('quoteArea');
        area?.classList.toggle('hidden');
    }

    // 切换标签区域
    toggleTagsArea() {
        const area = document.getElementById('tagsArea');
        area?.classList.toggle('hidden');
    }

    // 切换点赞
    toggleLike(thoughtId) {
        const thought = this.thoughtCells.find(t => t.id === thoughtId);
        if (!thought) return;
        
        thought.isLiked = !thought.isLiked;
        thought.likesCount = (thought.likesCount || 0) + (thought.isLiked ? 1 : -1);
        
        // 更新UI
        this.updateThoughtUI(thoughtId);
        
        // 保存到本地存储
        Storage.set('thought_cells', this.thoughtCells);
    }

    // 切换收藏
    toggleSave(thoughtId) {
        const thought = this.thoughtCells.find(t => t.id === thoughtId);
        if (!thought) return;
        
        thought.isSaved = !thought.isSaved;
        
        // 更新UI
        this.updateThoughtUI(thoughtId);
        
        // 保存到本地存储
        Storage.set('thought_cells', this.thoughtCells);
    }

    // 更新思想元胞UI
    updateThoughtUI(thoughtId) {
        const element = document.querySelector(`[data-thought-id="${thoughtId}"]`);
        if (!element) return;
        
        const thought = this.thoughtCells.find(t => t.id === thoughtId);
        if (!thought) return;
        
        // 重新渲染该思想元胞
        const container = element.parentNode;
        const index = Array.from(container.children).indexOf(element);
        element.remove();
        
        this.addThoughtCellToPage(thought);
        
        // 移动到原位置
        const newElement = container.lastElementChild;
        if (index < container.children.length - 1) {
            container.insertBefore(newElement, container.children[index]);
        }
    }

    // 编辑思想元胞
    editThought(thoughtId) {
        const thought = this.thoughtCells.find(t => t.id === thoughtId);
        if (!thought) return;
        
        // 填充编辑表单
        document.getElementById('thoughtContent').value = thought.content;
        document.getElementById('thoughtQuote').value = thought.quote || '';
        document.getElementById('thoughtTags').value = thought.tags?.join(', ') || '';
        
        // 显示相关区域
        if (thought.quote) document.getElementById('quoteArea')?.classList.remove('hidden');
        if (thought.tags?.length) document.getElementById('tagsArea')?.classList.remove('hidden');
        
        // 滚动到编辑区域
        document.getElementById('thoughtContent')?.scrollIntoView({ behavior: 'smooth' });
        setTimeout(() => document.getElementById('thoughtContent')?.focus(), 500);
    }

    // 删除思想元胞
    deleteThought(thoughtId) {
        if (!confirm('确定要删除这条思想元胞吗？')) return;
        
        try {
            // 从数组中删除
            this.thoughtCells = this.thoughtCells.filter(t => t.id !== thoughtId);
            
            // 保存到localStorage
            Storage.set('thought_cells', this.thoughtCells);
            
            // 更新统计
            if (this.currentUser?.stats && this.currentUser.stats.thoughts_count > 0) {
                this.currentUser.stats.thoughts_count--;
                this.updateUserStats();
            }
            
            // 重新渲染
            this.renderThoughtCells();
            
            Toast.success('思想元胞已删除');
        } catch (error) {
            console.error('删除失败:', error);
            Toast.error('删除失败: ' + error.message);
        }
    }

    // 评论思想元胞
    commentThought(thoughtId) {
        Toast.info('评论功能开发中...');
    }

    // 分享思想元胞
    shareThought(thoughtId) {
        const thought = this.thoughtCells.find(t => t.id === thoughtId);
        if (!thought) return;
        
        const shareText = `我在云己分享了一个思想元胞：${Utils.truncateText(thought.content, 50)}`;
        const shareUrl = `${window.location.origin}${window.location.pathname}?thought=${thoughtId}`;
        
        if (navigator.share) {
            navigator.share({
                title: '我的思想元胞',
                text: shareText,
                url: shareUrl
            }).then(() => {
                Toast.success('分享成功！');
            }).catch(() => {
                this.fallbackShare(shareText, shareUrl);
            });
        } else {
            this.fallbackShare(shareText, shareUrl);
        }
    }

    // 备用分享方法
    fallbackShare(text, url) {
        // 复制到剪贴板
        if (navigator.clipboard) {
            navigator.clipboard.writeText(`${text} ${url}`).then(() => {
                Toast.success('链接已复制到剪贴板');
            });
        } else {
            // 打开新窗口分享
            window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(url)}`);
        }
    }

    // 打开编辑资料模态框
    openEditModal() {
        Toast.info('编辑资料功能开发中...');
    }

    // 分享个人资料
    shareProfile() {
        const shareText = `查看我在云己的个人主页：${this.currentUser?.username || '云己用户'}`;
        const shareUrl = window.location.href;
        
        this.fallbackShare(shareText, shareUrl);
    }

    // 登出
    logout() {
        if (confirm('确定要登出吗？')) {
            Auth.logout();
        }
    }

    // 创建测试数据
    createTestThoughts() {
        const testThoughts = [
            {
                id: Date.now().toString(),
                content: '今天思考了关于数字永生的意义，人类的意识真的可以在数字世界中得到延续吗？',
                tags: ['数字永生', '哲学思考'],
                createdAt: new Date().toISOString(),
                likesCount: 0,
                commentsCount: 0,
                isLiked: false,
                isSaved: false
            },
            {
                id: (Date.now() + 1).toString(),
                content: '记录生活中的每一个瞬间，或许这就是构建个人数字意识体的第一步。',
                quote: '凡是过往，皆为序章。',
                tags: ['生活记录', '意识体'],
                createdAt: new Date(Date.now() - 3600000).toISOString(), // 1小时前
                likesCount: 1,
                commentsCount: 0,
                isLiked: true,
                isSaved: false
            }
        ];
        
        this.thoughtCells = [...testThoughts, ...this.thoughtCells];
        Storage.set('thought_cells', this.thoughtCells);
        
        // 更新统计
        if (this.currentUser?.stats) {
            this.currentUser.stats.thoughts_count += testThoughts.length;
            this.updateUserStats();
        }
        
        this.renderThoughtCells();
        Toast.success('测试数据创建成功！');
    }

    // 打开图片模态框
    openImageModal(imageUrl) {
        Toast.info('图片查看功能开发中...');
    }

    // 初始化组件
    initializeComponents() {
        // 可以在这里初始化其他组件
        console.log('个人主页初始化完成');
    }
}

// 创建全局实例
const homepage = new Homepage();

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    homepage.init();
});

// 导出到全局
window.homepage = homepage;